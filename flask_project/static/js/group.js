function createGroup() {
    // Agregar registro de equipo
    document.querySelector("#modal_content > button.agregar").addEventListener("click", () => {
        document.querySelector("#modal_content > div").innerHTML += `
        <div class="newTeam">
            <input class="modal_input" type="text" placeholder="nombre del equipo">
            <input class="modal_input" type="number" max="10" placeholder="integrantes">
        </div>
        `;
    });

    // Crear un grupo
    document.querySelector("#modal_content > button.crear").addEventListener("click", () => {
        let info = {};
        let name = document.querySelector("#modal_content > input.periodo").value + "-"; 
        name += document.querySelector("#modal_content > input.nombre").value + "-"; 
        name += document.querySelector("#modal_content > input.nrc").value; 
        info["name"] = name;
        const teams = document.querySelector("#modal_content > div").children;
        info["teamList"] = [];
        for(const team of teams) {
            info["teamList"].push([team.firstElementChild.value, team.lastElementChild.value]);
        }
        info = JSON.stringify(info);
        fetch("/api/create_group?data="+info)
        .then(data => data.json())
        .then(data => {
            if(data['success'] === true)
                alert(data["message"])
        });
    });

}

async function SelectGroup(){
    let container = document.querySelector("#modal_content > div");

    //Busca los grupos que tiene el usuario
    await fetch("/api/group")
    .then(data => data.json())
    .then(data => {
        if(!data["success"]){
            const visual_group = `<p>Error en el servidor...</p>`;
            container.innerHTML += visual_group;
            return;
        }
        data = data["data"]["grupos"];
        if(data.length === 0){
            const visual_group = `<p>No hay grupos disponibles</p>`;
            container.innerHTML += visual_group;
            return;
        }

        // Desplegando todos los grupos
        for (const group of data){
            let elem = document.createElement('p');
            elem.innerHTML = group[0];
            elem.classList.add("group_game");
            // Evento de click
            elem.addEventListener("click", () => {
                document.querySelectorAll(".group_game").forEach(e => e.removeAttribute("selected"));
                elem.setAttribute("selected", "")
                elem.dataset.group_id = group[1]
            });
            container.appendChild(elem);
        }
    });

    // Manda a pedir la info del grupo
    document.querySelector("#modal_content > button.play").addEventListener("click", () => {
        // Tomar el id del grupo
        const selectedGroup = document.querySelector("#modal_content > div > .group_game[selected]");
        if(selectedGroup === null)
            return;
        const groupId = selectedGroup.dataset.group_id;
        document.location.href=`/${groupId}`
    });

}