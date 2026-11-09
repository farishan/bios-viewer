document.querySelectorAll('.tab').forEach(function(t){t.addEventListener('click',function(){
  document.querySelectorAll('.tab').forEach(function(x){x.setAttribute('aria-selected',x===t)});
  document.querySelectorAll('.panel').forEach(function(p){p.hidden=p.dataset.p!==t.dataset.t});
})});
document.getElementById('theme').addEventListener('click',function(){
  var r=document.documentElement,d=r.dataset.theme==='dark'||(!r.dataset.theme&&matchMedia('(prefers-color-scheme: dark)').matches);
  r.dataset.theme=d?'light':'dark';
});
