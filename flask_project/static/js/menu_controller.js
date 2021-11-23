document.addEventListener("DOMContentLoaded", async () => {
    const animationFPS = 30;
    const frameDuration = 60 / animationFPS;
    const host = window.location.host; 

    const modalsContent = {
        "createGroup": `
                        <h2>Crear grupo:</h2>
                        <hr>
                        <br>
                        <input class="modal_input nombre" type="text" placeholder="nombre del grupo">
                        <input class="modal_input periodo" maxlength="6" type="text" placeholder="periodo">
                        <input class="modal_input nrc" maxlength="5" type="text" placeholder="nrc">

                        <div>
                            <div class="newTeam">
                                <input class="modal_input" type="text" placeholder="nombre del equipo">
                                <input class="modal_input" type="number" max="10" placeholder="integrantes">
                            </div>
                        </div>

                        <button class="button crear">Crear Grupo</button>
                        <button class="button agregar">Agregar equipo</button>  
                    `,
        "selectGame": `
                        <h2>Selecciona un juego:</h2>
                        <hr/>
                        <br>
                        <div></div>
                        <button class="button play">Jugar</button>
                        `,
        "configs":     `
                        <form action="/change_db" method="POST">
                            <input type="text" placeholder="host" name="host" required>
                            <input type="text" placeholder="user" name="user" required>
                            <input type="password" placeholder="password" name="password" required>
                            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                            <input class="button" type="submit" value="Enviar Cambios">
                        </form>
                    `
    };
    
    // ##### Events #####
    // Navbar animacion de entrada y salida
    document.querySelector("#navbar_toggle").addEventListener("click", function(){
        const menu = document.getElementById("navbar");
        const overlay = document.getElementById("overlay");

        if(!menu.classList.toggle("isOpen")){

            for (let i = 0; i < animationFPS; i++){
                setTimeout(() => {
                    const pixels2Move = (i+1)*(menu.clientWidth / animationFPS);
                    menu.style.left = `-${pixels2Move}px`;
                },
                frameDuration);
            }
            this.innerHTML = "Menú";
            overlay.style.visibility = "hidden";
        } else {
            menu.style.left = "0";
            this.innerHTML = "Cerrar";
            overlay.style.visibility = "visible";
        }
        overlay.classList.toggle("display");
    });

    //#####Menu EVENTS#####
    if(document.querySelector("#navbar_menu") !== null){
        // Crear grupo
        document.querySelector("#create_group").addEventListener("click", () => {
            openGeneralModal(modalsContent["createGroup"])
            createGroup();
        });
    
        //  Seleccionar grupo
        document.querySelector("#play_game").addEventListener("click", () => {
            openGeneralModal(modalsContent["selectGame"])
            SelectGroup();
        });

        //  Configuracion de la base de datos
        document.querySelector("#configs").addEventListener("click", () => {
            openGeneralModal(modalsContent["configs"])
        });

        //  Generar historial de sesion
        let opcionHistorialSesion = document.getElementById("session_history");
        if(opcionHistorialSesion !== null)
            opcionHistorialSesion.addEventListener("click", async () => {
                await fetch("/api/session_historial")
                .then(data => data.json())
                .then(data => {
                    data = data["data"];
                    if(data === null || data.lenght === 0) return;
                    let content = "";
                    for (const entry of data) {
                        let entryData = `<h4>ID: ${entry["id"]} -> ${entry["equipo"]}</h4>`;
                        entryData += `<p>Pregunta: ${entry["pregunta"]}</p>`;
                        entryData += `<p>Resultado: ${entry["resultado"]}</p>`;
                        entryData += "<hr>";
                        content += entryData;
                    }

                    openGeneralModal(content);
                });
            })

            //  Generar historial de sesion
            let opcionHistorialGrupo = document.getElementById("group_history");
            if(opcionHistorialGrupo !== null)
                opcionHistorialGrupo.addEventListener("click", async () => {
                    await fetch("/api/group_historial")
                    .then(data => data.json())
                    .then(data => {
                        data = data["data"];
                        if(data === null || data.lenght === 0) return;
                        let content = "";
                        let sessionNumber = 1;
                        for (const session of data) {
                            let entryData = `<h2>--- Sesion ${sessionNumber} ---</h2>`
                            for (const entry of session) {
                                entryData += `<h4>ID: ${entry["id"]} -> ${entry["equipo"]}</h4>`;
                                entryData += `<p>Pregunta: ${entry["pregunta"]}</p>`;
                                entryData += `<p>Resultado: ${entry["resultado"]}</p>`;
                                entryData += "<hr>";
                            }
                            console.log(entryData);
                            content += entryData;
                            sessionNumber++;
                        }
                        openGeneralModal(content);
                    });
                })
    }

    //#####General Modal Events#####
    // Mostrar GeneralModal
    function openGeneralModal(content) {
        let modal = document.querySelector("#modal_content");
        modal.innerHTML = content;
        document.querySelector("#modal").style.display = "block";
    }

    // Ocultar General Modal
    document.querySelector("#modal_close").addEventListener("click", () => {
        document.querySelector("#modal_content").innerHTML = "";
        document.getElementById("modal").style.display = "none";
    });
    


    handleLogin();
    EnableGame();
    NewRound();
});