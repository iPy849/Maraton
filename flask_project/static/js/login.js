function handleLogin() {
  // #####login Events######

  // Mostrar LoginModal
  const loginButton = document.querySelector("#user_info button.button.login");
  if (loginButton !== null)
    loginButton.addEventListener("click", () => {
      document.getElementById("login_modal").style.display = "block";
    });

  // Ocultar Modal login_close
  document.querySelector("#login_close").addEventListener("click", () => {
    document.getElementById("login_modal").style.display = "none";
  });

  // Comprobar que existe un usuario
  document.querySelector("#user_email").addEventListener("change", function () {
    fetch("/api/check_user/" + this.value)
      .then((data) => data.json())
      .then((data) => {
        const exists = data["data"]["exists"];
        if (exists)
          document.querySelector("#login_form > p").innerHTML =
            "Existe un usuario con esta dirección de email";
        else document.querySelector("#login_form > p").innerHTML = "";
      });
  });

  // Login
  document.querySelector("#login_button").addEventListener("click", () => {
    document.getElementById("auth_operation").value = "login";
    document.getElementById("login_form").submit();
  });

  // Register
  document.querySelector("#register_button").addEventListener("click", () => {
    document.getElementById("auth_operation").value = "register";
    if (document.querySelector("#login_form > p").innerHTML === "")
      document.getElementById("login_form").submit();
  });

  // Logout
  document
    .querySelector("#user_info button.button.logout")
    .addEventListener("click", () => {
      window.location.href = "/logout";
    });
}
