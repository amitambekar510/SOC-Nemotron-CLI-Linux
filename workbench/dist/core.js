(function(root){
  "use strict";
  function buildPrompt(workflow, values, notes="") {
    const missing=workflow.fields.filter(field=>!String(values[field.key]||"").trim()).map(field=>field.label);
    const text=workflow.prompt.replace(/\{\{([A-Z_]+)\}\}/g, (match,key)=>String(values[key]||"").trim()||match);
    return {text:text+(notes.trim()?"\n\nAdditional instructions:\n"+notes.trim():""),missing};
  }
  const api={buildPrompt};
  if(typeof module!=="undefined"&&module.exports) module.exports=api;
  else root.SOCWorkbench=api;
})(typeof window!=="undefined"?window:globalThis);
