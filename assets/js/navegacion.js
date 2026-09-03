(() => {
  "use strict";

  const botonMenu = document.querySelector("[data_boton_menu]");
  const navegacion = document.querySelector("[data_navegacion]");

  if (botonMenu && navegacion) {
    botonMenu.addEventListener("click", () => {
      const abierta = navegacion.classList.toggle("abierta");
      botonMenu.setAttribute("aria-expanded", String(abierta));
      botonMenu.textContent = abierta ? "Cerrar" : "Menú";
    });

    navegacion.addEventListener("click", (evento) => {
      if (evento.target.closest("a")) {
        navegacion.classList.remove("abierta");
        botonMenu.setAttribute("aria-expanded", "false");
        botonMenu.textContent = "Menú";
      }
    });
  }

  const indicador = document.querySelector("[data_progreso]");
  if (indicador) {
    const actualizarProgreso = () => {
      const altura = document.documentElement.scrollHeight - window.innerHeight;
      const porcentaje = altura > 0 ? Math.min(100, Math.max(0, (window.scrollY / altura) * 100)) : 0;
      indicador.style.width = `${porcentaje}%`;
    };
    actualizarProgreso();
    window.addEventListener("scroll", actualizarProgreso, { passive: true });
    window.addEventListener("resize", actualizarProgreso);
  }

  const usuario = document.querySelector("#tiene_usuario");
  const clave = document.querySelector("#tiene_clave");
  const resultado = document.querySelector("[data_resultado_logico]");

  if (usuario && clave && resultado) {
    const comprobarAcceso = () => {
      const acceso = usuario.checked && clave.checked;
      resultado.textContent = acceso
        ? "usuario AND contraseña = VERDADERO → acceso permitido"
        : "usuario AND contraseña = FALSO → acceso denegado";
      resultado.setAttribute("data_estado", acceso ? "verdadero" : "falso");
    };
    usuario.addEventListener("change", comprobarAcceso);
    clave.addEventListener("change", comprobarAcceso);
    comprobarAcceso();
  }
})();
