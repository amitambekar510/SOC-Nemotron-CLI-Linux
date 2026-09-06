const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {buildPrompt}=require('../workbench/dist/core.js');
const workflows=JSON.parse(fs.readFileSync(path.join(__dirname,'../examples/workflows.json'),'utf8'));

test('each workflow produces a complete prompt from its sample values',()=>{
  for(const workflow of workflows){
    const values=Object.fromEntries(workflow.fields.map(f=>[f.key,f.sample]));
    const result=buildPrompt(workflow,values);
    assert.deepEqual(result.missing,[]);
    assert.ok(!/\{\{[A-Z_]+\}\}/.test(result.text));
    for(const f of workflow.fields)assert.ok(result.text.includes(f.sample));
  }
});
test('blank required inputs keep placeholders and report missing labels',()=>{
  const workflow=workflows[0];
  const result=buildPrompt(workflow,{INPUT_FILE:'  '});
  assert.deepEqual(result.missing,workflow.fields.map(f=>f.label));
  assert.ok(result.text.includes('{{INPUT_FILE}}'));
});
test('values containing quotes, dollar signs and markup remain literal text',()=>{
  const payload='case "A" $(touch marker) <script>alert(1)</script> $& {{OUTPUT_FILE}}';
  const result=buildPrompt(workflows[0],{INPUT_FILE:payload,OUTPUT_FILE:'report.json'},'  check time zone  ');
  assert.ok(result.text.includes(payload));
  assert.ok(result.text.endsWith('Additional instructions:\ncheck time zone'));
});
test('rendering does not mutate the catalog',()=>{
  const before=JSON.stringify(workflows);
  buildPrompt(workflows[0],{INPUT_FILE:'sample.log',OUTPUT_FILE:'test.json'});
  assert.equal(JSON.stringify(workflows),before);
});
