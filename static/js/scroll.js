function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

document.addEventListener("DOMContentLoaded", function () {
    let page = 2;
    let actPage = page;
    const loader = document.getElementById("loader");
    const orderList = document.getElementById("order-list");
    const container = document.querySelector(".scroll-container");

    const orderBy = getUrlParameter('order_by') || 'delivery_date';
    const selectBy = getUrlParameter('select_by') || '';

    loader.style.display = "table-row";  // Lo hacemos visible inicialmente solo para la prueba

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (page != actPage) {
                loader.style.display = "table-row";
                actPage += 1;
            }
            if (entry.isIntersecting) {
                loader.style.display = "table-row";
                console.log("Is intersecting:", entry.isIntersecting); 
                loadMoreOrders();
            }
        });
    }, { root: container, threshold: 1 });

    observer.observe(loader);

    function loadMoreOrders() {
        console.log("Cargando más órdenes, página:", page);
        loader.style.display = "table-row";
        fetch(`?page=${page}&order_by=${orderBy}&select_by=${selectBy}`, { headers: { "x-requested-with": "XMLHttpRequest" } })
            .then(response => {
                if (!response.ok) throw new Error("Network response was not ok");
                return response.json();
            })
            .then(data => {
                if (data.orders.trim() === "") {
                    observer.disconnect();
                    console.log("No hay más órdenes para cargar.");
                } else {
                    orderList.insertAdjacentHTML("beforeend", data.orders);
                    page += 1;
                }
            })
            .catch(error => console.error("Error al cargar más órdenes:", error))
            .finally(() => loader.style.display = "none");
    }
});
