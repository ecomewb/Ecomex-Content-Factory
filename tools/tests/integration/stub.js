const Module=require('module'); const orig=Module._load;
Module._load=function(req,...a){ if(['sqlite3','better-sqlite3','@napi-rs/canvas','canvas','isolated-vm'].includes(req)) return new Proxy(function(){},{get:()=>new Proxy(function(){},{get:()=>()=>{}}),construct:()=>({})}); return orig.call(this,req,...a); };
