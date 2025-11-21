const form = document.getElementById("form-cadastro");
const msg = document.getElementById("msg");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const senha = document.getElementById("senha").value;
    const confirmarSenha = document.getElementById("confirmar_senha").value;

    // Confirmar Senha antes do cadastro
    if (senha !== confirmarSenha) {
        msg.innerText = "Senha incorreta";
        msg.style.color = "red";
        return;
    }

    const data = {
        nome: document.getElementById("nome").value,
        email: document.getElementById("email").value,
        senha: senha,
        ano_escolar: document.getElementById("ano_escolar").value
    };

    msg.innerText = "Enviando...";
    msg.style.color = "black";

    try {
        const response = await fetch("endereço da api", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data)
        });

        const resultado = await response.json();

        if (response.ok) {
            msg.innerText = "Usuário cadastrado com sucesso!";
            msg.style.color = "green";
        } else {
            msg.innerText = "Erro: " + resultado.error;
            msg.style.color = "red";
        }

    }catch (error) {
        msg.innerText = "Erro ao conectar com o servidor.";
        msg.style.color = "red";
    }
});