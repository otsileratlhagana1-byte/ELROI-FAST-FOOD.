
const KEY="elroi_cart";
function cart(){try{return JSON.parse(localStorage.getItem(KEY)||"[]")}catch(e){return[]}}
function saveCart(c){localStorage.setItem(KEY,JSON.stringify(c)); updateCartCount()}
function updateCartCount(){let n=cart().reduce((s,x)=>s+(+x.quantity||0),0);document.querySelectorAll("[data-cart-count]").forEach(e=>e.textContent=n)}
function addToCart(id,name,price,additions=[],removals=[]){
 let c=cart(), found=c.find(x=>x.id==id && JSON.stringify(x.additions)==JSON.stringify(additions) && JSON.stringify(x.removals)==JSON.stringify(removals));
 if(found) found.quantity++; else c.push({id,name,price:+price,quantity:1,additions,removals});
 saveCart(c); alert(name+" added to your cart."); 
}
function removeItem(i){let c=cart();c.splice(i,1);saveCart(c);renderCart()}
function changeQty(i,d){let c=cart();c[i].quantity=Math.max(1,c[i].quantity+d);saveCart(c);renderCart()}
function renderCart(){
 let box=document.querySelector("#cart-items"), totalEl=document.querySelector("#cart-total"); if(!box)return;
 let c=cart(); if(!c.length){box.innerHTML='<div class="notice">Your cart is empty. <a href="/menu"><b>Browse the menu</b></a>.</div>'; if(totalEl)totalEl.textContent="R0.00";return}
 let total=0; box.innerHTML=c.map((x,i)=>{let t=x.price*x.quantity;total+=t;return `<div class="form" style="margin-bottom:12px"><b>${x.name}</b><div class="muted">R${x.price.toFixed(2)} each</div>${x.additions?.length?`<small>Add: ${x.additions.join(", ")}</small>`:""}${x.removals?.length?`<small>Remove: ${x.removals.join(", ")}</small>`:""}<div style="display:flex;gap:8px;align-items:center;margin-top:10px"><button class="btn light" onclick="changeQty(${i},-1)">−</button><b>${x.quantity}</b><button class="btn light" onclick="changeQty(${i},1)">+</button><button class="btn secondary" onclick="removeItem(${i})">Remove</button></div></div>`}).join("");
 if(totalEl)totalEl.textContent="R"+total.toFixed(2);
}
document.addEventListener("DOMContentLoaded",()=>{updateCartCount();renderCart();});
