async function api(path, method = "GET", body = null) {
  const opts = { method, headers: { "Content-Type": "application/json" } }
  if (body) opts.body = JSON.stringify(body)
  const res = await fetch("/api" + path, opts)
  return res.json()
}

// Products CRUD UI

async function loadProducts() {
  const p = await api("/products")
  const el = document.getElementById("products")
  if (!p || p.error) { el.innerHTML = "<i>Помилка завантаження</i>"; return [] }
  el.innerHTML = p.map(x => `
      <div data-id="${x.id}">
        <b>${x.sku}</b> — ${x.name} (${x.unit})
        <button class="small-btn" onclick="editProduct(${x.id})"><svg viewBox="0 0 640 640" width="20" height="20""><path d="M100.4 417.2C104.5 402.6 112.2 389.3 123 378.5L304.2 197.3L338.1 163.4C354.7 180 389.4 214.7 442.1 267.4L476 301.3L442.1 335.2L260.9 516.4C250.2 527.1 236.8 534.9 222.2 539L94.4 574.6C86.1 576.9 77.1 574.6 71 568.4C64.9 562.2 62.6 553.3 64.9 545L100.4 417.2zM156 413.5C151.6 418.2 148.4 423.9 146.7 430.1L122.6 517L209.5 492.9C215.9 491.1 221.7 487.8 226.5 483.2L155.9 413.5zM510 267.4C493.4 250.8 458.7 216.1 406 163.4L372 129.5C398.5 103 413.4 88.1 416.9 84.6C430.4 71 448.8 63.4 468 63.4C487.2 63.4 505.6 71 519.1 84.6L554.8 120.3C568.4 133.9 576 152.3 576 171.4C576 190.5 568.4 209 554.8 222.5C551.3 226 536.4 240.9 509.9 267.4z"/></svg></button>
        <button class="small-btn" onclick="deleteProduct(${x.id})"><svg viewBox="0 0 640 640" width="20" height="20""><path d="M232.7 69.9C237.1 56.8 249.3 48 263.1 48L377 48C390.8 48 403 56.8 407.4 69.9L416 96L512 96C529.7 96 544 110.3 544 128C544 145.7 529.7 160 512 160L128 160C110.3 160 96 145.7 96 128C96 110.3 110.3 96 128 96L224 96L232.7 69.9zM128 208L512 208L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 208zM216 272C202.7 272 192 282.7 192 296L192 488C192 501.3 202.7 512 216 512C229.3 512 240 501.3 240 488L240 296C240 282.7 229.3 272 216 272zM320 272C306.7 272 296 282.7 296 296L296 488C296 501.3 306.7 512 320 512C333.3 512 344 501.3 344 488L344 296C344 282.7 333.3 272 320 272zM424 272C410.7 272 400 282.7 400 296L400 488C400 501.3 410.7 512 424 512C437.3 512 448 501.3 448 488L448 296C448 282.7 437.3 272 424 272z" /></svg></button></button>
      </div>`).join("")
  return p
}

async function createProduct(form) {
  const body = { sku: form.sku.value.trim(), name: form.name.value.trim(), unit: form.unit.value.trim() }
  const r = await api("/products", "POST", body)
  if (r.error) alert(r.error)
  else { form.reset(); loadProducts() }
}
async function editProduct(id) {
  const data = await api("/products/" + id)
  if (data.error) { alert(data.error); return }
  const form = document.getElementById("product-edit-form")
  form.elements["id"].value = data.id
  form.elements["sku"].value = data.sku
  form.elements["name"].value = data.name
  form.elements["unit"].value = data.unit
  form.style.display = "block"
}
async function saveEditProduct(e) {
  e.preventDefault()
  const f = e.target
  const id = f.elements["id"].value
  const body = { sku: f.elements["sku"].value.trim(), name: f.elements["name"].value.trim(), unit: f.elements["unit"].value.trim() }
  const r = await api("/products/" + id, "PUT", body)
  if (r.error) alert(r.error)
  else { f.style.display = "none"; loadProducts() }
}
async function deleteProduct(id) {
  if (!confirm("Видалити товар? Це неможливо якщо вже є транзакції.")) return
  const r = await api("/products/" + id, "DELETE")
  if (r.error) alert(r.error)
  else loadProducts()
}

// Locations CRUD UI

async function loadLocations() {
  const p = await api("/locations")
  const el = document.getElementById("locations")
  if (!p || p.error) { el.innerHTML = "<i>Помилка завантаження</i>"; return [] }
  el.innerHTML = p.map(x => `
  <div data-id="${x.id}">
    <b>${x.code}</b> — ${x.description || ''}
    <button class="small-btn" onclick="editLocation(${x.id})"><svg viewBox="0 0 640 640" width="20" height="20""><path d="M100.4 417.2C104.5 402.6 112.2 389.3 123 378.5L304.2 197.3L338.1 163.4C354.7 180 389.4 214.7 442.1 267.4L476 301.3L442.1 335.2L260.9 516.4C250.2 527.1 236.8 534.9 222.2 539L94.4 574.6C86.1 576.9 77.1 574.6 71 568.4C64.9 562.2 62.6 553.3 64.9 545L100.4 417.2zM156 413.5C151.6 418.2 148.4 423.9 146.7 430.1L122.6 517L209.5 492.9C215.9 491.1 221.7 487.8 226.5 483.2L155.9 413.5zM510 267.4C493.4 250.8 458.7 216.1 406 163.4L372 129.5C398.5 103 413.4 88.1 416.9 84.6C430.4 71 448.8 63.4 468 63.4C487.2 63.4 505.6 71 519.1 84.6L554.8 120.3C568.4 133.9 576 152.3 576 171.4C576 190.5 568.4 209 554.8 222.5C551.3 226 536.4 240.9 509.9 267.4z"/></svg></button>
    <button class="small-btn" onclick="deleteLocation(${x.id})"><svg viewBox="0 0 640 640" width="20" height="20""><path d="M232.7 69.9C237.1 56.8 249.3 48 263.1 48L377 48C390.8 48 403 56.8 407.4 69.9L416 96L512 96C529.7 96 544 110.3 544 128C544 145.7 529.7 160 512 160L128 160C110.3 160 96 145.7 96 128C96 110.3 110.3 96 128 96L224 96L232.7 69.9zM128 208L512 208L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 208zM216 272C202.7 272 192 282.7 192 296L192 488C192 501.3 202.7 512 216 512C229.3 512 240 501.3 240 488L240 296C240 282.7 229.3 272 216 272zM320 272C306.7 272 296 282.7 296 296L296 488C296 501.3 306.7 512 320 512C333.3 512 344 501.3 344 488L344 296C344 282.7 333.3 272 320 272zM424 272C410.7 272 400 282.7 400 296L400 488C400 501.3 410.7 512 424 512C437.3 512 448 501.3 448 488L448 296C448 282.7 437.3 272 424 272z"/></svg></button>
  </div>`).join("")
  return p
}
async function createLocation(form) {
  const body = { code: form.code.value.trim(), description: form.desc.value.trim() }
  const r = await api("/locations", "POST", body)
  if (r.error) alert(r.error)
  else { form.reset(); loadLocations() }
}
async function editLocation(id) {
  const data = await api("/locations/" + id)
  if (data.error) { alert(data.error); return }
  const form = document.getElementById("location-edit-form")
  form.elements["id"].value = data.id
  form.elements["code"].value = data.code
  form.elements["description"].value = data.description || ""
  form.style.display = "block"
}
async function saveEditLocation(e) {
  e.preventDefault()
  const f = e.target
  const id = f.elements["id"].value
  const body = { code: f.elements["code"].value.trim(), description: f.elements["description"].value.trim() }
  const r = await api("/locations/" + id, "PUT", body)
  if (r.error) alert(r.error)
  else { f.style.display = "none"; loadLocations() }
}
async function deleteLocation(id) {
  if (!confirm("Видалити локацію?")) return
  const r = await api("/locations/" + id, "DELETE")
  if (r.error) alert(r.error)
  else loadLocations()
}

// Stock / transactions UI

async function loadStock() {
  const s = await api("/stock")
  const tbody = document.querySelector("#stock-table tbody")
  tbody.innerHTML = s.map(r => `<tr><td>${r.sku}</td><td>${r.name}</td><td>${r.location}</td><td>${r.batch || ""}</td><td>${r.quantity}</td></tr>`).join("")
}
async function loadTrans() {
  const t = await api("/transactions")
  const el = document.getElementById("transactions")
  el.innerHTML = "<ol>" + t.map(x => `<li>[${x.ts}] ${x.type} ${x.sku} ${x.qty} @ ${x.location || "-"} ${x.batch || ""}</li>`).join("") + "</ol>"
}

// Forms for receive/pick and creation
document.getElementById("product-form").addEventListener("submit", async e=>{ e.preventDefault(); createProduct(e.target) })
document.getElementById("location-form").addEventListener("submit", async e=>{ e.preventDefault(); createLocation(e.target) })
document.getElementById("product-edit-form").addEventListener("submit", saveEditProduct)
document.getElementById("location-edit-form").addEventListener("submit", saveEditLocation)

document.getElementById("receive-form").addEventListener("submit", async e => {
  e.preventDefault()
  const f = e.target
  const body = { sku: f.sku.value.trim(), location: f.location.value.trim(), qty: parseInt(f.qty.value), batch: f.batch.value.trim() || null }
  const r = await api("/receive", "POST", body)
  if (r.error) alert(r.error)
  f.reset(); loadStock(); loadTrans()
})
document.getElementById("pick-form").addEventListener("submit", async e => {
  e.preventDefault()
  const f = e.target
  const body = { sku: f.sku.value.trim(), location: f.location.value.trim() || null, qty: parseInt(f.qty.value), batch: f.batch.value.trim() || null }
  const r = await api("/pick", "POST", body)
  if (r.error) alert(r.error)
  f.reset(); loadStock(); loadTrans()
})

document.getElementById("refresh-stock").addEventListener("click", loadStock)
document.getElementById("refresh-trans").addEventListener("click", loadTrans)

// initial load
loadProducts(); loadLocations(); loadStock(); loadTrans()
