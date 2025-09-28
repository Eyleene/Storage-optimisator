async function api(path, method = "GET", body = null) {
  const opts = { method, headers: { "Content-Type": "application/json" } }
  if (body) opts.body = JSON.stringify(body)
  const res = await fetch("/api" + path, opts)
  return res.json()
}

// Products CRUD UI

let productPage = 1;
const productLimit = 10;
let allProducts = [];

async function loadProducts(page = 1) {
  const el = document.getElementById("products");

  // Якщо ще не завантажили всі продукти, підтягуємо
  if (allProducts.length === 0) {
    const p = await api("/products");
    if (!p || p.error) {
      el.innerHTML = "<i>Помилка завантаження</i>";
      return [];
    }
    allProducts = p;
  }

  const totalPages = Math.ceil(allProducts.length / productLimit);
  productPage = Math.min(Math.max(1, page), totalPages);

  const start = (productPage - 1) * productLimit;
  const end = start + productLimit;
  const pageItems = allProducts.slice(start, end);

  el.innerHTML = pageItems.map(x =>
    `<div data-id="${x.id}" class="list">
      <div>
        <b>${x.sku}</b> — ${x.name} (${x.unit})
      </div>
      <div>
        <button class="small-btn" onclick="editProduct(${x.id})"><svg alt="Редагувати" viewBox="0 0 640 640" width="20" height="20""><path d="M100.4 417.2C104.5 402.6 112.2 389.3 123 378.5L304.2 197.3L338.1 163.4C354.7 180 389.4 214.7 442.1 267.4L476 301.3L442.1 335.2L260.9 516.4C250.2 527.1 236.8 534.9 222.2 539L94.4 574.6C86.1 576.9 77.1 574.6 71 568.4C64.9 562.2 62.6 553.3 64.9 545L100.4 417.2zM156 413.5C151.6 418.2 148.4 423.9 146.7 430.1L122.6 517L209.5 492.9C215.9 491.1 221.7 487.8 226.5 483.2L155.9 413.5zM510 267.4C493.4 250.8 458.7 216.1 406 163.4L372 129.5C398.5 103 413.4 88.1 416.9 84.6C430.4 71 448.8 63.4 468 63.4C487.2 63.4 505.6 71 519.1 84.6L554.8 120.3C568.4 133.9 576 152.3 576 171.4C576 190.5 568.4 209 554.8 222.5C551.3 226 536.4 240.9 509.9 267.4z"/></svg></button>
        <button class="small-btn" onclick="deleteProduct(${x.id})"><svg alt="Видалити" viewBox="0 0 640 640" width="20" height="20""><path d="M232.7 69.9C237.1 56.8 249.3 48 263.1 48L377 48C390.8 48 403 56.8 407.4 69.9L416 96L512 96C529.7 96 544 110.3 544 128C544 145.7 529.7 160 512 160L128 160C110.3 160 96 145.7 96 128C96 110.3 110.3 96 128 96L224 96L232.7 69.9zM128 208L512 208L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 208zM216 272C202.7 272 192 282.7 192 296L192 488C192 501.3 202.7 512 216 512C229.3 512 240 501.3 240 488L240 296C240 282.7 229.3 272 216 272zM320 272C306.7 272 296 282.7 296 296L296 488C296 501.3 306.7 512 320 512C333.3 512 344 501.3 344 488L344 296C344 282.7 333.3 272 320 272zM424 272C410.7 272 400 282.7 400 296L400 488C400 501.3 410.7 512 424 512C437.3 512 448 501.3 448 488L448 296C448 282.7 437.3 272 424 272z" /></svg></button></button>
      </div>
    </div>`).join("");

  // Пагінація
  const pagination = document.createElement("div");
  pagination.innerHTML =
    `<div class="pagination">
      <button class="small-btn" ${productPage <= 1 ? 'disabled' : ''} onclick="loadProducts(${productPage - 1})"><svg alt="Попередня" viewBox="0 0 640 640" width="20" height="20""><path d="M73.4 297.4C60.9 309.9 60.9 330.2 73.4 342.7L233.4 502.7C245.9 515.2 266.2 515.2 278.7 502.7C291.2 490.2 291.2 469.9 278.7 457.4L173.3 352L544 352C561.7 352 576 337.7 576 320C576 302.3 561.7 288 544 288L173.3 288L278.7 182.6C291.2 170.1 291.2 149.8 278.7 137.3C266.2 124.8 245.9 124.8 233.4 137.3L73.4 297.3z"/></svg></button>
      <span>  Сторінка ${productPage} з ${totalPages}  </span>

      <button class="small-btn" ${productPage >= totalPages ? 'disabled' : ''} onclick="loadProducts(${productPage + 1})"><svg alt="Наступна" viewBox="0 0 640 640" width="20" height="20""><path d="M566.6 342.6C579.1 330.1 579.1 309.8 566.6 297.3L406.6 137.3C394.1 124.8 373.8 124.8 361.3 137.3C348.8 149.8 348.8 170.1 361.3 182.6L466.7 288L96 288C78.3 288 64 302.3 64 320C64 337.7 78.3 352 96 352L466.7 352L361.3 457.4C348.8 469.9 348.8 490.2 361.3 502.7C373.8 515.2 394.1 515.2 406.6 502.7L566.6 342.7z"/></svg></button>
    </div>`;
  el.appendChild(pagination);
}


async function createProduct(form) {
  const body = { sku: form.sku.value.trim(), name: form.name.value.trim(), unit: form.unit.value.trim() }
  const r = await api("/products", "POST", body)
  if (r.error) alert(r.error)
  else {
    form.reset();
    allProducts = []; // очищаємо кеш
    loadProducts();
  }
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
let locationPage = 1;
const locationLimit = 10;
let allLocations = [];

async function loadLocations(page = 1) {
  const el = document.getElementById("locations");

  if (allLocations.length === 0) {
    const l = await api("/locations");
    if (!l || l.error) {
      el.innerHTML = "<i>Помилка завантаження</i>";
      return [];
    }
    allLocations = l;
  }

  const totalPages = Math.ceil(allLocations.length / locationLimit);
  locationPage = Math.min(Math.max(1, page), totalPages); // <-- тут page має значення

  const start = (locationPage - 1) * locationLimit;
  const end = start + locationLimit;
  const pageItems = allLocations.slice(start, end);

  el.innerHTML = pageItems.map(x => `
    <div data-id="${x.id}" class="list">
      <div><b>${x.code}</b> — ${x.description || ''}</div>
      <div>
        <button class="small-btn" onclick="editLocation(${x.id})"><svg viewBox="0 0 640 640" width="20" height="20""><path d="M100.4 417.2C104.5 402.6 112.2 389.3 123 378.5L304.2 197.3L338.1 163.4C354.7 180 389.4 214.7 442.1 267.4L476 301.3L442.1 335.2L260.9 516.4C250.2 527.1 236.8 534.9 222.2 539L94.4 574.6C86.1 576.9 77.1 574.6 71 568.4C64.9 562.2 62.6 553.3 64.9 545L100.4 417.2zM156 413.5C151.6 418.2 148.4 423.9 146.7 430.1L122.6 517L209.5 492.9C215.9 491.1 221.7 487.8 226.5 483.2L155.9 413.5zM510 267.4C493.4 250.8 458.7 216.1 406 163.4L372 129.5C398.5 103 413.4 88.1 416.9 84.6C430.4 71 448.8 63.4 468 63.4C487.2 63.4 505.6 71 519.1 84.6L554.8 120.3C568.4 133.9 576 152.3 576 171.4C576 190.5 568.4 209 554.8 222.5C551.3 226 536.4 240.9 509.9 267.4z"/></svg></button>
        <button class="small-btn" onclick="deleteLocation(${x.id})"><svg viewBox="0 0 640 640" width="20" height="20""><path d="M232.7 69.9C237.1 56.8 249.3 48 263.1 48L377 48C390.8 48 403 56.8 407.4 69.9L416 96L512 96C529.7 96 544 110.3 544 128C544 145.7 529.7 160 512 160L128 160C110.3 160 96 145.7 96 128C96 110.3 110.3 96 128 96L224 96L232.7 69.9zM128 208L512 208L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 208zM216 272C202.7 272 192 282.7 192 296L192 488C192 501.3 202.7 512 216 512C229.3 512 240 501.3 240 488L240 296C240 282.7 229.3 272 216 272zM320 272C306.7 272 296 282.7 296 296L296 488C296 501.3 306.7 512 320 512C333.3 512 344 501.3 344 488L344 296C344 282.7 333.3 272 320 272zM424 272C410.7 272 400 282.7 400 296L400 488C400 501.3 410.7 512 424 512C437.3 512 448 501.3 448 488L448 296C448 282.7 437.3 272 424 272z"/></svg></button>
      </div>
    </div>`).join("");

  // Пагінація
  const pagination = document.createElement("div");
  pagination.innerHTML =
    `<div class="pagination">
      <button class="small-btn" ${productPage <= 1 ? 'disabled' : ''} onclick="loadProducts(${productPage - 1})"><svg alt="Попередня" viewBox="0 0 640 640" width="20" height="20""><path d="M73.4 297.4C60.9 309.9 60.9 330.2 73.4 342.7L233.4 502.7C245.9 515.2 266.2 515.2 278.7 502.7C291.2 490.2 291.2 469.9 278.7 457.4L173.3 352L544 352C561.7 352 576 337.7 576 320C576 302.3 561.7 288 544 288L173.3 288L278.7 182.6C291.2 170.1 291.2 149.8 278.7 137.3C266.2 124.8 245.9 124.8 233.4 137.3L73.4 297.3z"/></svg></button>
      <span>  Сторінка ${productPage} з ${totalPages}  </span>

      <button class="small-btn" ${productPage >= totalPages ? 'disabled' : ''} onclick="loadProducts(${productPage + 1})"><svg alt="Наступна" viewBox="0 0 640 640" width="20" height="20""><path d="M566.6 342.6C579.1 330.1 579.1 309.8 566.6 297.3L406.6 137.3C394.1 124.8 373.8 124.8 361.3 137.3C348.8 149.8 348.8 170.1 361.3 182.6L466.7 288L96 288C78.3 288 64 302.3 64 320C64 337.7 78.3 352 96 352L466.7 352L361.3 457.4C348.8 469.9 348.8 490.2 361.3 502.7C373.8 515.2 394.1 515.2 406.6 502.7L566.6 342.7z"/></svg></button>
    </div>`;
  el.appendChild(pagination);

}

async function createLocation(form) {
  const body = { code: form.code.value.trim(), description: form.desc.value.trim() }
  const r = await api("/locations", "POST", body)
  if (r.error) alert(r.error)
  else {
    form.reset();
    allLocations = []; // очищаємо кеш
    loadLocations();
  }
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
  else {
    f.style.display = "none"
    allLocations = []; // очищаємо кеш
    loadLocations()
  }
}
async function deleteLocation(id) {
  if (!confirm("Видалити локацію?")) return
  const r = await api("/locations/" + id, "DELETE")
  if (r.error) alert(r.error)
  else {
    allLocations = []; // очищаємо кеш
    loadLocations()
  }
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
document.getElementById("product-form").addEventListener("submit", async e => { e.preventDefault(); createProduct(e.target) })
document.getElementById("location-form").addEventListener("submit", async e => { e.preventDefault(); createLocation(e.target) })
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
