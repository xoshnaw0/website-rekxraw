(function(){
"use strict";
var I18N = window.I18N || {}, LS = "chyakan_lang", code = "ckb";
var NAVKEY = { about:"navAbout", programs:"navPrograms", impact:"navImpact", contact:"navContact" };
var MONTHS = ["کانوونی دووەم","شوبات","ئازار","نیسان","ئایار","حوزەیران","تەممووز","ئاب","ئەیلوول","تشرینی یەکەم","تشرینی دووەم","کانوونی یەکەم"];
var SAFE_IMG = /^(?:images|\/media)\/[\w\-\/.]+\.(?:jpe?g|png|webp)$/i;
function q(s){ return document.querySelector(s); }
function qa(s){ return Array.prototype.slice.call(document.querySelectorAll(s)); }

/* text is always inserted as text nodes (never innerHTML); only <em> is allowed */
function rich(el, str){
  el.textContent = "";
  var re = /<em>(.*?)<\/em>/g, last = 0, m;
  while((m = re.exec(str))){
    if(m.index > last) el.appendChild(document.createTextNode(str.slice(last, m.index)));
    var e = document.createElement("em"); e.textContent = m[1]; el.appendChild(e); last = re.lastIndex;
  }
  if(last < str.length) el.appendChild(document.createTextNode(str.slice(last)));
}

function apply(c){
  var d = I18N[c]; if(!d) return; code = c;
  var h = document.documentElement; h.lang = d.lang; h.dir = d.dir;
  qa("[data-i18n]").forEach(function(el){ var k = el.getAttribute("data-i18n"); if(d[k] !== undefined) rich(el, d[k]); });
  qa("[data-i18n-aria]").forEach(function(el){ var k = el.getAttribute("data-i18n-aria"); if(d[k]) el.setAttribute("aria-label", d[k]); });
  qa(".lang-switch button").forEach(function(b){ var on = b.getAttribute("data-lang") === c; b.classList.toggle("active", on); b.setAttribute("aria-pressed", on ? "true" : "false"); });
  var p = document.body.getAttribute("data-page");
  document.title = d.brandName + (NAVKEY[p] ? " — " + d[NAVKEY[p]] : "");
  try{ localStorage.setItem(LS, c); }catch(e){}
  renderActs();
}
qa(".lang-switch button").forEach(function(b){ b.addEventListener("click", function(){ apply(b.getAttribute("data-lang")); }); });

/* mobile menu */
var drawer = q("#drawer"), menuBtn = q(".menu-btn");
function setMenu(o){
  drawer.classList.toggle("open", o); drawer.setAttribute("aria-hidden", o ? "false" : "true");
  menuBtn.setAttribute("aria-expanded", o ? "true" : "false"); document.body.classList.toggle("noscroll", o);
}
if(drawer && menuBtn){
  menuBtn.addEventListener("click", function(){ setMenu(true); });
  q(".drawer-close").addEventListener("click", function(){ setMenu(false); });
  q(".drawer-bg").addEventListener("click", function(){ setMenu(false); });
  qa("#drawer a").forEach(function(a){ a.addEventListener("click", function(){ setMenu(false); }); });
  document.addEventListener("keydown", function(e){ if(e.key === "Escape") setMenu(false); });
}

/* activities */
function pick(o){ return (o && (o[code] || o.ckb || o.en)) || ""; }
function fmt(iso){
  var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || ""); if(!m) return "";
  var d = new Date(+m[1], +m[2]-1, +m[3]); if(isNaN(d)) return "";
  if(code === "ckb") return +m[3] + " " + MONTHS[+m[2]-1] + " " + m[1];
  try{ return d.toLocaleDateString(code === "ar" ? "ar-IQ" : "en-GB", {year:"numeric", month:"long", day:"numeric"}); }catch(e){ return iso; }
}
var lb, lbImg, lbList = [], lbI = 0;
function lbShow(){ lbImg.src = lbList[lbI]; }
function openLb(list, i){
  if(!lb){
    lb = document.createElement("div"); lb.className = "lb"; lb.setAttribute("role", "dialog"); lb.setAttribute("aria-modal", "true");
    lbImg = document.createElement("img"); lbImg.alt = "";
    [["x","✕",function(){ lb.classList.remove("open"); }],["pv","‹",function(){ lbI = (lbI + lbList.length - 1) % lbList.length; lbShow(); }],["nx","›",function(){ lbI = (lbI + 1) % lbList.length; lbShow(); }]].forEach(function(t){
      var b = document.createElement("button"); b.type = "button"; b.className = t[0]; b.textContent = t[1]; b.addEventListener("click", t[2]); lb.appendChild(b);
    });
    lb.appendChild(lbImg);
    lb.addEventListener("click", function(e){ if(e.target === lb) lb.classList.remove("open"); });
    document.addEventListener("keydown", function(e){
      if(!lb.classList.contains("open")) return;
      if(e.key === "Escape") lb.classList.remove("open");
      if(e.key === "ArrowLeft") lb.querySelector(".pv").click();
      if(e.key === "ArrowRight") lb.querySelector(".nx").click();
    });
    document.body.appendChild(lb);
  }
  lbList = list; lbI = i; lbShow(); lb.classList.add("open");
  lb.querySelectorAll(".pv,.nx").forEach(function(b){ b.style.display = list.length > 1 ? "" : "none"; });
}
function renderActs(){
  qa("[data-acts]").forEach(function(box){
    var mode = box.getAttribute("data-acts"), sec = box.closest("section");
    var list = (window.ACTIVITIES || []).filter(function(a){ return a && /^\d{4}-\d{2}-\d{2}$/.test(a.date || ""); })
      .sort(function(a, b){ return a.date < b.date ? 1 : -1; });
    if(mode === "latest") list = list.slice(0, 3);
    box.textContent = "";
    if(!list.length){
      if(mode === "latest"){ if(sec) sec.hidden = true; return; }
      var p = document.createElement("p"); p.className = "empty"; p.textContent = (I18N[code] || {}).noActs || ""; box.appendChild(p); return;
    }
    if(sec) sec.hidden = false;
    var grid = document.createElement("div"); grid.className = "acts";
    list.forEach(function(a){
      var imgs = (a.images || []).filter(function(s){ return typeof s === "string" && SAFE_IMG.test(s); });
      var title = pick(a.title), card = document.createElement("article"); card.className = "act";
      if(imgs.length){
        var cb = document.createElement("button"); cb.type = "button"; cb.className = "act-cover";
        var im = document.createElement("img"); im.src = imgs[0]; im.alt = title; im.loading = "lazy"; cb.appendChild(im);
        cb.addEventListener("click", function(){ openLb(imgs, 0); }); card.appendChild(cb);
      }
      var body = document.createElement("div"); body.className = "act-body";
      var dt = document.createElement("div"); dt.className = "act-date"; dt.textContent = fmt(a.date);
      var h = document.createElement("h3"); h.textContent = title;
      var tx = document.createElement("p"); tx.textContent = pick(a.text);
      body.appendChild(dt); body.appendChild(h); if(tx.textContent) body.appendChild(tx); card.appendChild(body);
      if(imgs.length > 1){
        var th = document.createElement("div"); th.className = "act-thumbs";
        imgs.forEach(function(s, i){
          var b = document.createElement("button"); b.type = "button"; var t = document.createElement("img"); t.src = s; t.alt = ""; t.loading = "lazy";
          b.appendChild(t); b.addEventListener("click", function(){ openLb(imgs, i); }); th.appendChild(b);
        });
        card.appendChild(th);
      }
      grid.appendChild(card);
    });
    box.appendChild(grid);
  });
}

/* contact form: no server. Opens the visitor's email app addressed to the organization. */
var form = q("#contactForm");
if(form){
  var t0 = Date.now(), status = q("#formStatus");
  form.addEventListener("submit", function(e){
    e.preventDefault();
    if(form.company.value || Date.now() - t0 < 2000) return; /* honeypot / too fast = bot */
    var name = form.name.value.trim().slice(0,120), email = form.email.value.trim().slice(0,180), msg = form.message.value.trim().slice(0,1500);
    var d = I18N[code] || I18N.ckb;
    if(!name || !msg || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)){ status.textContent = d.formErr; status.className = "form-status err"; return; }
    status.textContent = "…"; status.className = "form-status";
    var tok = (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || "";
    fetch(form.getAttribute("data-action"), { method:"POST", body:new FormData(form), headers:{ "X-CSRFToken": tok }, credentials:"same-origin" })
      .then(function(r){ if(!r.ok) throw 0; status.textContent = d.formOk; status.className = "form-status ok"; form.reset(); })
      .catch(function(){ status.textContent = d.formFail; status.className = "form-status err"; });
  });
}

/* CV form: uploads the file to the server (stored privately, only staff can open it) */
var cvForm = q("#cvForm");
if(cvForm){
  var t1 = Date.now(), cs = q("#cvStatus");
  cvForm.addEventListener("submit", function(e){
    e.preventDefault();
    if(cvForm.company.value || Date.now() - t1 < 2000) return;
    var d = I18N[code] || I18N.ckb, f = cvForm.cv.files[0];
    function bad(t){ cs.textContent = t; cs.className = "form-status err"; }
    if(!cvForm.name.value.trim() || !cvForm.phone.value.trim() || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(cvForm.email.value.trim())) return bad(d.cErr);
    if(!f || !/\.(pdf|docx?)$/i.test(f.name) || f.size > 5 * 1024 * 1024) return bad(d.cBadFile);
    var tok = (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || "";
    cs.textContent = "…"; cs.className = "form-status";
    fetch(cvForm.getAttribute("data-action"), { method:"POST", body:new FormData(cvForm), headers:{ "X-CSRFToken": tok }, credentials:"same-origin" })
      .then(function(r){ if(!r.ok) throw 0; cs.textContent = d.cOk; cs.className = "form-status ok"; cvForm.reset(); })
      .catch(function(){ bad(d.formFail); });
  });
}

var saved = "ckb"; try{ saved = localStorage.getItem(LS) || "ckb"; }catch(e){}
apply(I18N[saved] ? saved : "ckb");
})();
