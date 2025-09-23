    async function api(path, method="GET", body=null){
      const opts = {method, headers:{"Content-Type":"application/json"}}
      if(body) opts.body = JSON.stringify(body)
      const res = await fetch("/api"+path, opts)
      return res.json()
    }

    async function loadProducts(){
      const p = await api("/products")
      const el = document.getElementById("products")
      el.innerHTML = "<ul>"+p.map(x=>`<li>${x.sku} — ${x.name} (${x.unit})</li>`).join("")+"</ul>"
      return p
    }
    async function loadLocations(){
      const p = await api("/locations")
      const el = document.getElementById("locations")
      el.innerHTML = "<ul>"+p.map(x=>`<li>${x.code} — ${x.description||''}</li>`).join("")+"</ul>"
      return p
    }
    async function loadStock(){
      const s = await api("/stock")
      const tbody = document.querySelector("#stock-table tbody")
      tbody.innerHTML = s.map(r=>`<tr><td>${r.sku}</td><td>${r.name}</td><td>${r.location}</td><td>${r.batch||""}</td><td>${r.quantity}</td></tr>`).join("")
    }
    async function loadTrans(){
      const t = await api("/transactions")
      const el = document.getElementById("transactions")
      el.innerHTML = "<ol>"+t.map(x=>`<li>[${x.ts}] ${x.type} ${x.sku} ${x.qty} @ ${x.location||"-"} ${x.batch||""}</li>`).join("")+"</ol>"
    }

    document.getElementById("product-form").addEventListener("submit", async e=>{
      e.preventDefault()
      const f = e.target
      const body = {sku: f.sku.value.trim(), name: f.name.value.trim(), unit: f.unit.value.trim()}
      await api("/products","POST",body)
      f.reset(); loadProducts()
    })
    document.getElementById("location-form").addEventListener("submit", async e=>{
      e.preventDefault()
      const f = e.target
      const body = {code: f.code.value.trim(), description: f.desc.value.trim()}
      await api("/locations","POST",body)
      f.reset(); loadLocations()
    })
    document.getElementById("receive-form").addEventListener("submit", async e=>{
      e.preventDefault()
      const f = e.target
      const body = {sku:f.sku.value.trim(), location:f.location.value.trim(), qty: parseInt(f.qty.value), batch:f.batch.value.trim()||null}
      const r = await api("/receive","POST",body)
      if(r.error) alert(r.error)
      f.reset(); loadStock(); loadTrans()
    })
    document.getElementById("pick-form").addEventListener("submit", async e=>{
      e.preventDefault()
      const f = e.target
      const body = {sku:f.sku.value.trim(), location:f.location.value.trim()||null, qty: parseInt(f.qty.value), batch:f.batch.value.trim()||null}
      const r = await api("/pick","POST",body)
      if(r.error) alert(r.error)
      f.reset(); loadStock(); loadTrans()
    })

    document.getElementById("refresh-stock").addEventListener("click", loadStock)
    document.getElementById("refresh-trans").addEventListener("click", loadTrans)

    // initial load
    loadProducts(); loadLocations(); loadStock(); loadTrans()
