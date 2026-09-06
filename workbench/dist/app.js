"use strict";
const $=id=>document.getElementById(id);
const workflows=window.SOC_WORKFLOWS;
const drafts=new Map();
let selected=workflows[0];
function values(){return Object.fromEntries(selected.fields.map(f=>[f.key,$(f.key).value]));}
function remember(){drafts.set(selected.id,{values:values(),notes:$("notes").value});}
function update(){
  const result=SOCWorkbench.buildPrompt(selected,values(),$("notes").value);
  $("preview").value=result.text;
  $("readiness").textContent=result.missing.length?`${selected.fields.length-result.missing.length}/${selected.fields.length} fields ready`:"Ready to review";
  $("copy").disabled=$("download").disabled=!!result.missing.length;
  $("status").textContent=result.missing.length?"Complete: "+result.missing.join(", "):"";
  remember();
}
function select(workflow){
  selected=workflow;
  const draft=drafts.get(workflow.id)||{values:{},notes:""};
  $("workflow-title").textContent=workflow.title;$("description").textContent=workflow.description;$("level").textContent=workflow.level;
  $("fields").replaceChildren();
  for(const f of workflow.fields){
    const label=document.createElement("label");label.htmlFor=f.key;label.textContent=f.label;
    const input=document.createElement("input");input.id=f.key;input.required=true;input.maxLength=500;input.value=draft.values[f.key]||"";input.placeholder=f.sample;input.autocomplete="off";input.setAttribute("aria-describedby",f.key+"-hint");
    const hint=document.createElement("p");hint.id=f.key+"-hint";hint.className="hint";hint.textContent=f.hint;
    $("fields").append(label,input,hint);
  }
  $("notes").value=draft.notes;$("review-list").replaceChildren();
  for(const item of workflow.review){const li=document.createElement("li");li.textContent=item;$("review-list").append(li);}
  document.querySelectorAll("nav button").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.id===workflow.id)));
  update();
}
for(const workflow of workflows){
  const button=document.createElement("button");button.type="button";button.dataset.id=workflow.id;
  const title=document.createElement("strong");title.textContent=workflow.title;
  const hint=document.createElement("small");hint.textContent=workflow.category;
  button.append(title,hint);button.addEventListener("click",()=>select(workflow));$("workflows").append(button);
}
$("context-form").addEventListener("input",update);$("context-form").addEventListener("submit",e=>e.preventDefault());
$("sample").addEventListener("click",()=>{for(const f of selected.fields)$(f.key).value=f.sample;update();$("status").textContent="Sample filenames only. No evidence has been loaded.";});
$("reset").addEventListener("click",()=>{drafts.delete(selected.id);select(selected);});
$("copy").addEventListener("click",async()=>{
  try{await navigator.clipboard.writeText($("preview").value);$("status").textContent="Prompt copied. Paste it into your OpenCode session.";}
  catch{$("preview").focus();$("preview").select();$("status").textContent="Clipboard unavailable. Use Ctrl+C or Cmd+C to copy the selected prompt.";}
});
$("download").addEventListener("click",()=>{
  const blob=new Blob([`# ${selected.title}\n\n${$("preview").value}\n`],{type:"text/markdown;charset=utf-8"});
  const url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download=selected.id+"-prompt.md";document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);$("status").textContent="Prompt downloaded. Review before use.";
});
select(selected);
