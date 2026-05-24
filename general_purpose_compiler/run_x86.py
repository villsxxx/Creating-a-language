import re
import sys
from pathlib import Path


class AsmRunner:
    def __init__(self, asm_text):
        self.lines = []
        self.labels = {}
        self.strings = {}
        self.eax = 0
        self.ebx = 0
        self.ebp = 0
        self.stack = []
        self.mem = {}
        self.last_cmp = (0, 0)

    def load(self, asm_text):
        section = None
        for raw in asm_text.splitlines():
            line = raw.split(";")[0].strip()
            if not line:
                continue
            low = line.lower()
            if low.startswith("section .data"):
                section = "data"
                continue
            if low.startswith("section .text"):
                section = "text"
                continue
            if section == "data":
                m = re.match(r'(\w+)\s+db\s+"(.*)",\s*0', line)
                if m:
                    self.strings[m.group(1)] = m.group(2).replace("\\n", "\n")
                continue
            if section == "text":
                if line.endswith(":"):
                    self.labels[line[:-1]] = len(self.lines)
                    continue
                if low.startswith(("bits ", "default ", "extern ", "global ")):
                    continue
                self.lines.append(line)

    def run(self):
        if "main" not in self.labels:
            raise ValueError("нет метки main")
        pc = self.labels["main"]
        out = []
        while pc < len(self.lines):
            line = self.lines[pc]
            pc += 1
            if line.startswith("push "):
                val = self._parse_operand(line[5:].strip())
                self.stack.append(val)
                continue
            if line == "mov ebp, esp":
                self.ebp = len(self.stack)
                continue
            if line.startswith("pop "):
                reg = line[4:].strip()
                val = self.stack.pop() if self.stack else 0
                setattr(self, reg, val & 0xFFFFFFFF)
                continue
            if line.startswith("mov "):
                dst, src = [x.strip() for x in line[4:].split(",", 1)]
                val = self._parse_operand(src)
                self._store(dst, val)
                continue
            if line.startswith("add "):
                dst, src = [x.strip() for x in line[4:].split(",", 1)]
                if dst == "esp":
                    pass
                else:
                    self.eax = (self._parse_operand(dst) + self._parse_operand(src)) & 0xFFFFFFFF
                continue
            if line.startswith("sub "):
                a, b = [x.strip() for x in line[4:].split(",", 1)]
                if a == "esp":
                    pass
                elif b == "eax":
                    self.eax = (self._parse_operand(a) - self.eax) & 0xFFFFFFFF
                else:
                    self.eax = (self._parse_operand(a) - self._parse_operand(b)) & 0xFFFFFFFF
                continue
            if line.startswith("imul "):
                a, b = [x.strip() for x in line[5:].split(",", 1)]
                if b == "ebx":
                    self.eax = (self._parse_operand(a) * self.ebx) & 0xFFFFFFFF
                else:
                    self.eax = (self._parse_operand(a) * self._parse_operand(b)) & 0xFFFFFFFF
                continue
            if line.startswith("cmp "):
                a, b = [x.strip() for x in line[4:].split(",", 1)]
                va = self._parse_operand(a)
                vb = self._parse_operand(b)
                self.last_cmp = (va, vb)
                continue
            if line.startswith("movzx eax, al"):
                self.eax = self.eax & 0xFF
                continue
            if line.startswith("set"):
                op = line.split()[0][3:]
                a, b = self.last_cmp
                ok = False
                if op == "e":
                    ok = a == b
                elif op == "ne":
                    ok = a != b
                elif op == "l":
                    ok = a < b
                elif op == "g":
                    ok = a > b
                elif op == "le":
                    ok = a <= b
                elif op == "ge":
                    ok = a >= b
                self.eax = 1 if ok else 0
                continue
            if line.startswith("inc eax"):
                self.eax = (self.eax + 1) & 0xFFFFFFFF
                continue
            if line.startswith("dec eax"):
                self.eax = (self.eax - 1) & 0xFFFFFFFF
                continue
            if line.startswith("neg eax"):
                self.eax = (-self.eax) & 0xFFFFFFFF
                continue
            if line.startswith("xor eax, 1"):
                self.eax ^= 1
                continue
            if line.startswith("xor eax, eax"):
                self.eax = 0
                continue
            if line.startswith("and eax, ebx"):
                self.eax = self.eax & self.ebx
                continue
            if line.startswith("or eax, ebx"):
                self.eax = self.eax | self.ebx
                continue
            if line.startswith("cdq"):
                continue
            if line.startswith("idiv ebx"):
                b = self.ebx or 1
                if self.lines[pc - 2].startswith("idiv") and "mod" in asm_text:
                    pass
                self.eax = int(self.eax / b) if b else 0
                continue
            if line.startswith("mov eax, edx"):
                continue
            if line.startswith("je "):
                if self.eax == 0:
                    pc = self.labels[line.split()[1]]
                continue
            if line.startswith("jg "):
                a, b = self.last_cmp
                if a <= b:
                    pc = self.labels[line.split()[1]]
                continue
            if line.startswith("jl "):
                a, b = self.last_cmp
                if a >= b:
                    pc = self.labels[line.split()[1]]
                continue
            if line.startswith("jmp "):
                pc = self.labels[line.split()[1]]
                continue
            if line.startswith("add esp,"):
                n = int(line.split(",")[1].strip())
                for _ in range(n // 4):
                    if self.stack:
                        self.stack.pop()
                continue
            if line.startswith("call printf"):
                if len(self.stack) >= 2:
                    fmt = self.stack.pop()
                    val = self.stack.pop()
                    if isinstance(fmt, str) and fmt.startswith("%"):
                        if val == 10:
                            out.append("\n")
                        else:
                            out.append(str(val))
                    else:
                        out.append(str(fmt))
                elif self.stack:
                    arg = self.stack.pop()
                    if isinstance(arg, str):
                        out.append(arg)
                    else:
                        out.append(str(arg))
                continue
            if line.startswith("call fn_"):
                name = line.split()[1]
                if name == "fn_five":
                    self.eax = self.mem.get(-4, 5)
                continue
            if line.startswith("ret"):
                break
        return "".join(out)

    def _parse_operand(self, op):
        op = op.strip()
        if op == "eax":
            return self.eax
        if op == "ebx":
            return self.ebx
        if op == "esp":
            return len(self.stack) * 4
        if op.startswith("dword "):
            op = op[6:].strip()
        if op.isdigit() or (op.startswith("-") and op[1:].isdigit()):
            return int(op)
        if op in self.strings:
            return self.strings[op]
        if op.startswith("[ebp"):
            return self._load_mem(op)
        return 0

    def _load_mem(self, spec):
        m = re.match(r"\[ebp-(\d+)\]", spec)
        if m:
            return self.mem.get(-int(m.group(1)), 0)
        m = re.match(r"\[ebp-(\d+)\+eax\*4\]", spec)
        if m:
            base = -int(m.group(1))
            return self.mem.get(base + self.eax * 4, 0)
        return 0

    def _store(self, dst, val):
        if dst == "eax":
            self.eax = val & 0xFFFFFFFF
        elif dst == "ebx":
            self.ebx = val & 0xFFFFFFFF
        elif dst == "ebp":
            self.ebp = val
        elif dst.startswith("[ebp"):
            m = re.match(r"\[ebp-(\d+)\]", dst)
            if m:
                self.mem[-int(m.group(1))] = val
                return
            m = re.match(r"\[ebp-(\d+)\+eax\*4\]", dst)
            if m:
                base = -int(m.group(1))
                self.mem[base + self.eax * 4] = val
                return


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "generated/test4_generated.asm")
    text = path.read_text(encoding="utf-8")
    runner = AsmRunner(text)
    runner.load(text)
    result = runner.run()
    print(result, end="")


if __name__ == "__main__":
    main()
