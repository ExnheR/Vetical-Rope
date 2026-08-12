document.addEventListener("DOMContentLoaded", () => {

    /*==========================
    MODO OSCURO
    ==========================*/

    const toggleBtn = document.getElementById("toggle-mode");
    const body = document.body;

    if (toggleBtn) {

        const icon = toggleBtn.querySelector("i");
        const modo = localStorage.getItem("modoVerticalRope");

        if (modo === "oscuro") {
            body.classList.add("dark-mode");

            if (icon) {
                icon.classList.remove("fa-moon");
                icon.classList.add("fa-sun");
            }
        }

        toggleBtn.addEventListener("click", () => {

            body.classList.toggle("dark-mode");

            const oscuro = body.classList.contains("dark-mode");

            if (icon) {
                icon.classList.toggle("fa-moon", !oscuro);
                icon.classList.toggle("fa-sun", oscuro);
            }

            localStorage.setItem(
                "modoVerticalRope",
                oscuro ? "oscuro" : "claro"
            );

        });
    }


    /*==========================
    TRANSICIÓN DE PÁGINA
    ==========================*/

    const transition = document.getElementById("page-transition");

    if (transition) {

        const links = document.querySelectorAll('a[href$=".html"]');

        links.forEach(link => {

            link.addEventListener("click", event => {

                const url = link.getAttribute("href");

                if (!url || url === "#") {
                    return;
                }

                if (link.target === "_blank") {
                    return;
                }

                event.preventDefault();

                transition.classList.add("show");

                setTimeout(() => {
                    window.location.href = url;
                }, 3000);

            });

        });
    }

});
```javascript
/* =========================================================
   CARRITO GLOBAL - VERTICAL ROPE
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       OBTENER CARRITO
       ===================================================== */

    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];


    /* =====================================================
       GUARDAR CARRITO
       ===================================================== */

    function guardarCarrito() {

        localStorage.setItem(
            "carrito",
            JSON.stringify(carrito)
        );

    }


    /* =====================================================
       ACTUALIZAR CONTADOR
       ===================================================== */

    function actualizarContador() {

        const contador = document.getElementById("cart-count");

        if (!contador) return;


        const cantidad = carrito.reduce(
            (total, producto) =>
                total + (producto.cantidad || 1),
            0
        );


        contador.textContent = cantidad;


        /* Ocultar contador cuando está vacío */

        if (cantidad === 0) {

            contador.style.display = "none";

        } else {

            contador.style.display = "flex";

        }

    }


    /* =====================================================
       AGREGAR PRODUCTO
       ===================================================== */

    document.querySelectorAll(".agregar-carrito")
        .forEach(boton => {

            boton.addEventListener("click", () => {

                const nombre = boton.dataset.name;


                if (!nombre) return;


                /* Buscar si ya existe */

                const productoExistente =
                    carrito.find(
                        producto =>
                            producto.nombre === nombre
                    );


                if (productoExistente) {

                    productoExistente.cantidad++;

                } else {

                    carrito.push({

                        nombre: nombre,

                        cantidad: 1

                    });

                }


                guardarCarrito();

                actualizarContador();


                /* ========================================
                   ANIMACIÓN DEL BOTÓN
                   ======================================== */

                const textoOriginal =
                    boton.innerHTML;


                boton.innerHTML =
                    '<i class="fas fa-check"></i> Agregado';


                boton.disabled = true;


                setTimeout(() => {

                    boton.innerHTML =
                        textoOriginal;

                    boton.disabled = false;

                }, 1000);


            });

        });


    /* =====================================================
       ACTUALIZAR AL CARGAR
       ===================================================== */

    actualizarContador();


    /* =====================================================
       HACER DISPONIBLE GLOBALMENTE
       ===================================================== */

    window.carrito = carrito;

    window.actualizarCarrito = actualizarContador;

    window.guardarCarrito = guardarCarrito;

});
```
