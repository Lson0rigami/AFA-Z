// ---------------------------------------------------------------------------
// REFERÊNCIAS GERAIS
// ---------------------------------------------------------------------------

// document.documentElement representa a tag <html>. O atributo data-theme
// colocado nela controla quais variáveis de cor themes.css vai aplicar.
const root = document.documentElement;
const themeWindow = document.querySelector("#theme-window");
const themeOptions = document.querySelectorAll("[data-theme-option]");

// Atualiza aria-pressed para que leitores de tela e o CSS saibam qual tema está
// selecionado. O operador || usa AMMO-8 quando nenhum tema tiver sido salvo.
function markCurrentTheme() {
    const currentTheme = root.dataset.theme || "ammo-8";

    themeOptions.forEach((option) => {
        option.setAttribute(
            "aria-pressed",
            String(option.dataset.themeOption === currentTheme)
        );
    });
}

// Todos os botões com data-open-theme abrem a mesma janela de temas. Verificar
// !themeWindow.open evita o erro de tentar abrir um <dialog> já aberto.
document.querySelectorAll("[data-open-theme]").forEach((button) => {
    button.addEventListener("click", () => {
        markCurrentTheme();
        if (themeWindow && !themeWindow.open) themeWindow.showModal();
    });
});

// data-theme-option contém o identificador usado no CSS, como "hollow".
// localStorage guarda apenas no navegador; não é uma informação do banco.
themeOptions.forEach((option) => {
    option.addEventListener("click", () => {
        const selectedTheme = option.dataset.themeOption;
        root.dataset.theme = selectedTheme;

        // Alguns navegadores podem bloquear o armazenamento. O try/catch deixa
        // a troca funcionar nesta visita mesmo quando não for possível salvar.
        try {
            localStorage.setItem("afa-z-theme", selectedTheme);
        } catch (error) {
            console.info("Não foi possível salvar o tema neste navegador.");
        }

        markCurrentTheme();
    });
});

// ---------------------------------------------------------------------------
// JANELAS DE CRIAÇÃO E FECHAMENTO DE DIALOGS
// ---------------------------------------------------------------------------

// Um botão data-dialog-target="new-task" procura #new-task e abre essa janela.
// Isso permite reutilizar a mesma lógica para tarefa, categoria e futuras telas.
document.querySelectorAll("[data-dialog-target]").forEach((button) => {
    button.addEventListener("click", () => {
        const dialog = document.querySelector(`#${button.dataset.dialogTarget}`);

        if (dialog) {
            if (!dialog.open) dialog.showModal();
            // Depois de abrir, o foco vai direto ao primeiro campo visível.
            const firstField = dialog.querySelector(
                "input:not([type='hidden']), textarea"
            );
            if (firstField) firstField.focus();
        }
    });
});

// closest("dialog") sobe pelos elementos pais até encontrar a janela à qual o
// botão pertence. Assim, cada botão fecha apenas sua própria janela.
document.querySelectorAll("[data-close-dialog]").forEach((button) => {
    button.addEventListener("click", () => {
        const dialog = button.closest("dialog");
        if (dialog && dialog.open) dialog.close();
    });
});

// O navegador entrega as coordenadas do clique. Comparamos com o retângulo da
// janela para fechar somente quando o clique realmente aconteceu do lado de fora.
document.querySelectorAll("dialog").forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
        const bounds = dialog.getBoundingClientRect();
        const clickedOutside =
            event.clientX < bounds.left ||
            event.clientX > bounds.right ||
            event.clientY < bounds.top ||
            event.clientY > bounds.bottom;

        if (clickedOutside && dialog.open) dialog.close();
    });
});

// ---------------------------------------------------------------------------
// DATA E RELÓGIO DO PAINEL
// ---------------------------------------------------------------------------

function updateDateAndTime() {
    const now = new Date();

    // Intl aplica a escrita e a ordem naturais do português brasileiro sem
    // precisarmos montar manualmente listas de dias e meses.
    const formattedDate = new Intl.DateTimeFormat("pt-BR", {
        weekday: "long",
        day: "2-digit",
        month: "long"
    }).format(now);

    const formattedTime = new Intl.DateTimeFormat("pt-BR", {
        hour: "2-digit",
        minute: "2-digit"
    }).format(now);

    document.querySelectorAll("[data-current-date]").forEach((element) => {
        element.textContent = formattedDate;
        element.setAttribute("datetime", now.toISOString().slice(0, 10));
    });

    document.querySelectorAll("[data-current-time]").forEach((element) => {
        element.textContent = formattedTime;
        element.setAttribute("datetime", formattedTime);
    });
}

// Executa uma vez assim que o arquivo carrega. Depois, o intervalo de 30
// segundos mantém o relógio atualizado sem recarregar a página inteira.
markCurrentTheme();
updateDateAndTime();
setInterval(updateDateAndTime, 30000);
