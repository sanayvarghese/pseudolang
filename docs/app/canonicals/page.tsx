import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "Canonical Structures" };

const DEFAULT_PMAP = `[FUNC_DEF]
func {name:name}({args:any})
function {name:name}({args:any})
define {name:name}({args:any})
def {name:name}({args:any})
procedure {name:name}({args:any})
algorithm {name:name}({args:any})
recursive {name:name}({args:any})

[FOR_LOOP]
for {var:name} from {start:expr} to {end:expr} step {step:expr}
for {var:name} from {start:expr} to {end:expr}
loop {var:name} from {start:expr} to {end:expr}
repeat {var:name} from {start:expr} to {end:expr}

[FOR_EACH]
for each {item:name} in {collection:expr}
for every {item:name} in {collection:expr}
for {item:name} in {collection:expr}
loop through {collection:expr} as {item:name}

[WHILE_LOOP]
while {condition:expr}
keep going while {condition:expr}
as long as {condition:expr}

[UNTIL_LOOP]
until {condition:expr}
repeat until {condition:expr}

[IF]
@context TOP_LEVEL FUNCTION_BODY LOOP_BODY IF_BODY
if {condition:expr}
when {condition:expr}
check {condition:expr}
given {condition:expr}

[ELSE_IF]
else if {condition:expr}
elif {condition:expr}
otherwise when {condition:expr}

[ELSE]
else
otherwise
if not

[RETURN]
return {value:expr}
give back {value:expr}
output {value:expr}
return

[BREAK]
break
stop
exit loop

[CONTINUE]
continue
skip
next

[PRINT]
print {value:expr}
show {value:expr}
display {value:expr}
say {value:expr}

[INPUT]
$input
$input as {type:word}
$input({prompt:any})
$input({prompt:any}) as {type:word}

[ASSIGN]
@context TOP_LEVEL FUNCTION_BODY LOOP_BODY IF_BODY
{var:name} = {value:expr}
{var:name} := {value:expr}
{var:name} <- {value:expr}
set {var:name} to {value:expr}
let {var:name} be {value:expr}
store {value:expr} in {var:name}
{var:name} is {value:expr}

[TRY]
try
attempt

[CATCH]
catch {error:name}
except {error:name}
catch
on error {error:name}

[FINALLY]
finally
always
cleanup

[RAISE]
raise {error:any}
throw {error:any}

[SWAP]
swap {a:expr} and {b:expr}
exchange {a:expr} and {b:expr}

[GLOBAL]
global {var:name}`;

export default function CanonicalsPage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          Language Reference › <span>Canonical Structures</span>
        </span>
        <span className="topbar-badge">v0.1</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">Language Reference</span>
          <h1 className="page-title">Canonical Structures</h1>
          <p className="page-desc">
            The fixed internal structures of Pseudo. These never change — only
            the surface syntax is customizable via <code>.pmap</code>.
          </p>
        </div>

        <div className="callout info">
          <span className="callout-icon">ℹ</span>
          <div className="callout-body">
            The default English patterns below are defined in{" "}
            <code>default.pmap</code> (ships with Pseudo, read-only). You can
            add more patterns via a custom pmap.
          </div>
        </div>

        <h2>Complete default.pmap</h2>
        <CodeBlock code={DEFAULT_PMAP} lang="text" title="default.pmap" />

        <h2>Context Flags</h2>
        <p>
          Some sections declare <code>@context</code> to resolve ambiguity. For
          example, <code>x is 5</code>:
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Context</th>
                <th>Pattern</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>TOP_LEVEL</td>
                <td>
                  <code>
                    {"{var:name}"} is {"{value:expr}"}
                  </code>{" "}
                  (ASSIGN)
                </td>
                <td>
                  <code>x is 5</code> → assignment
                </td>
              </tr>
              <tr>
                <td>CONDITION</td>
                <td>
                  <code>
                    {"{a:expr}"} is {"{b:expr}"}
                  </code>{" "}
                  (EQUALITY)
                </td>
                <td>
                  <code>if x is y</code> → equality check
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2>Range Behavior</h2>
        <CodeBlock
          lang="pseudo"
          code={`for i from 0 to 10    # → 0, 1, 2, ... 9 (10 is EXCLUSIVE)
for i from 10 to 0 step -1  # → 10, 9, 8, ... 1`}
        />
        <p>
          Step defaults to <code>1</code>. Backwards iteration requires an
          explicit negative step.
        </p>

        <h2>UNTIL Loop</h2>
        <CodeBlock
          lang="pseudo"
          code={`# "until" = loop WHILE condition is FALSE
repeat until x == 0
# equivalent to: while x != 0`}
        />

        <h2>Inline Blocks</h2>
        <p>
          Any block-starting line can have an inline body separated by a colon:
        </p>
        <CodeBlock
          lang="pseudo"
          code={`if n == 10: print "ten"
for i from 0 to 3: print i
while x < 3: x = x + 1
if true: if true: print "nested"`}
        />
      </div>
    </>
  );
}
