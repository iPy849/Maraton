function EnableGame() {
    // Variable de estado-resultado de ronda
    let roundResult = document.querySelector("#round_result");

    // Asignando los eventos de ganado, perdido y robado
    function cleanResultState(){
        document.querySelector("#round_win").classList.remove("button_highlighted");
        document.querySelector("#round_lose").classList.remove("button_highlighted");
        document.querySelector("label.button").classList.remove("button_highlighted");
    };

    document.querySelector("#round_win").addEventListener("click", () =>{
        cleanResultState();
        roundResult.value = -2;
        document.querySelector("#round_win").classList.add("button_highlighted");

    });

    document.querySelector("#round_lose").addEventListener("click", () =>{
        cleanResultState();
        roundResult.value = -1;
        document.querySelector("#round_lose").classList.add("button_highlighted");
    });

    document.querySelector("#round_steal").addEventListener("change", () =>{
        cleanResultState();
        roundResult.value = document.querySelector("#round_steal").value;
        document.querySelector("label.button").classList.add("button_highlighted");
    });

    document.querySelector("#end_round").addEventListener("click", (e) =>{
        if(roundResult.value === "-3"){
            e.preventDefault()
            return;
        }
        EndRound();
        cleanResultState();
    });

    document.querySelector("#end_session").addEventListener("click", () =>{
        window.location.href = "/end_session"
    });
    
    document.querySelector("#end_group").addEventListener("click", function(){
        window.location.href = "/end_group/" + this.dataset.id;
    });
}

async function EndRound(){
    let modal = document.querySelector("#modal_content");
    modal.innerHTML = 'Registrando ronda';
    document.querySelector("#modal").style.display = "block";
    document.querySelector("#modal_close").style.display = "none";

    const teams = Array.from(document.getElementById('teamList').children);
    let d_teams = document.getElementById("currentTeam");
    d_teams.dataset.team = parseInt(d_teams.dataset.team);
    let currentTeam = teams[d_teams.dataset.team % teams.length].dataset.id;
    currentTeam = parseInt(currentTeam);

    const questionId = document.querySelector("#currentQuestion").dataset.id;
    const roundResult = document.querySelector("#round_result");
    await fetch(`/end_round?question_id=${questionId}&team_id=${currentTeam}&result=${roundResult.value}`);
    document.querySelector("#modal").style.display = "none";
    document.querySelector("#modal_close").style.display = "block";

    NewRound();
    
}


async function NewRound(){
    let modal = document.querySelector("#modal_content");
    modal.innerHTML = 'Cargando pregunta';
    document.querySelector("#modal").style.display = "block";
    document.querySelector("#modal_close").style.display = "none";

    // Pregunta
    await fetch('/api/getQuestion')
    .then( data => data.json())
    .then( data => {
        data = data["data"];
        document.querySelector("#currentTopic").innerHTML = data["tema"];
        document.querySelector("#currentQuestion").innerHTML = data["pregunta"];
        document.querySelector("#currentQuestion").dataset.id = data["id"];
        document.querySelector("#currentAnswer").innerHTML = data["respuesta"];
    });

    // Equipo
    const teams = Array.from(document.getElementById('teamList').children);
    let d_teams = document.getElementById("currentTeam");
    d_teams.dataset.team = parseInt(d_teams.dataset.team) + 1;
    d_teams.innerText = teams[d_teams.dataset.team % teams.length].innerHTML;

    // Estadisticas del equipo
    const nextTeamId = teams[d_teams.dataset.team % teams.length].dataset.id;
    const currentSession = document.getElementById("game-session").dataset.session;

    await fetch(`/team_session_statistics?team_id=${nextTeamId}&session_id=${currentSession}`)
    .then(data => data.json())
    .then(data => {
        data = data["data"];
        document.getElementById("team_session_win").innerText = data["ganadas"];
        document.getElementById("team_session_lose").innerText = data["perdidas"];
        document.getElementById("team_session_stolen").innerText = data["robadas"];
        document.getElementById("team_session_qty").innerText = data["integrantes"];
        document.getElementById("team_session_total").innerText = data["total"];
    })

    // Habilitar Cerrar Grupo o Sesion
    document.getElementById("end_session").style.display = d_teams.dataset.team % teams.length === 0 ? "block" : "none";
    document.getElementById("end_group").style.display = d_teams.dataset.team % teams.length === 0 ? "block" : "none";
    document.querySelector("#round_result").value = "-3";

    document.querySelector("#modal").style.display = "none";
    document.querySelector("#modal_close").style.display = "block";
}