const API_URL = "http://127.0.0.1:8000";

const salasValidas = [
  "Sala 101 (Laboratório)",
  "Sala 102 (Teórica)",
  "Auditório A",
  "Bloco B - Sala 05",
];

const horariosValidos = [
  "08:00 - 10:00",
  "10:00 - 12:00",
  "14:00 - 16:00",
  "16:00 - 18:00",
];

let reservas = [];
let usandoApi = false;

const loginPanel = document.querySelector("#loginPanel");
const dashboard = document.querySelector("#dashboard");
const loginForm = document.querySelector("#loginForm");
const reservationForm = document.querySelector("#reservationForm");
const reservasLista = document.querySelector("#reservasLista");
const totalReservas = document.querySelector("#totalReservas");
const totalSalas = document.querySelector("#totalSalas");
const totalDisponiveis = document.querySelector("#totalDisponiveis");
const apiStatus = document.querySelector("#apiStatus");
const formMessage = document.querySelector("#formMessage");
const salaSelect = document.querySelector("#sala");
const horarioSelect = document.querySelector("#horario");
const dataReservaInput = document.querySelector("#dataReserva");
const responsavelInput = document.querySelector("#responsavel");
const logoutButton = document.querySelector("#logoutButton");
const calendarGrid = document.querySelector("#calendarGrid");
const selectedDateLabel = document.querySelector("#selectedDateLabel");
const previousDayButton = document.querySelector("#previousDayButton");
const nextDayButton = document.querySelector("#nextDayButton");
const ocupacaoChart = document.querySelector("#ocupacaoChart");
const notificationList = document.querySelector("#notificationList");
const menuButtons = document.querySelectorAll(".menu-button[data-target]");
const sidebarLogoutButton = document.querySelector("#sidebarLogoutButton");

function hojeFormatado() {
  return dataParaIso(new Date());
}

function dataParaIso(data) {
  const ano = data.getFullYear();
  const mes = String(data.getMonth() + 1).padStart(2, "0");
  const dia = String(data.getDate()).padStart(2, "0");
  return `${ano}-${mes}-${dia}`;
}

function formatarData(data) {
  const [ano, mes, dia] = data.split("-");
  return `${dia}/${mes}/${ano}`;
}

function preencherSelect(select, opcoes) {
  select.innerHTML = opcoes
    .map((opcao) => `<option value="${opcao}">${opcao}</option>`)
    .join("");
}

function mostrarMensagem(texto, tipo = "success") {
  formMessage.textContent = texto;
  formMessage.className = `form-message ${tipo}`;
}

function atualizarResumo() {
  const reservasDoDia = filtrarReservasDoDia();
  const totalSlots = salasValidas.length * horariosValidos.length;

  totalReservas.textContent = reservasDoDia.length;
  totalSalas.textContent = salasValidas.length;
  totalDisponiveis.textContent = totalSlots - reservasDoDia.length;
  apiStatus.textContent = usandoApi ? "API" : "Demo";
  selectedDateLabel.textContent = formatarData(dataReservaInput.value);
}

function filtrarReservasDoDia() {
  return reservas.filter(
    (reserva) => (reserva.data || dataReservaInput.value) === dataReservaInput.value,
  );
}

function renderizarReservas() {
  atualizarResumo();
  renderizarCalendario();
  renderizarGrafico();
  renderizarNotificacoes();

  const reservasDoDia = filtrarReservasDoDia();

  if (!reservasDoDia.length) {
    reservasLista.innerHTML =
      '<div class="empty-state">Nenhuma reserva cadastrada para esta data.</div>';
    return;
  }

  reservasLista.innerHTML = reservasDoDia
    .map(
      (reserva) => `
        <article class="reservation-item">
          <div>
            <strong>${reserva.sala}</strong>
            <p>${formatarData(reserva.data || dataReservaInput.value)} | ${reserva.horario} | Responsavel: ${reserva.responsavel}</p>
          </div>
          <button class="danger-button" type="button" data-id="${reserva.id}">
            Cancelar
          </button>
        </article>
      `,
    )
    .join("");
}

async function carregarReservas() {
  try {
    const resposta = await fetch(`${API_URL}/reservas`);

    if (!resposta.ok) {
      throw new Error("API indisponivel");
    }

    reservas = (await resposta.json()).map((reserva) => ({
      data: dataReservaInput.value,
      ...reserva,
    }));
    usandoApi = true;
  } catch {
    usandoApi = false;
    reservas = JSON.parse(localStorage.getItem("roomifyReservas") || "[]");
  }

  renderizarReservas();
}

function salvarDemo() {
  localStorage.setItem("roomifyReservas", JSON.stringify(reservas));
}

function existeConflito(sala, horario) {
  return reservas.some(
    (reserva) =>
      reserva.sala === sala &&
      reserva.horario === horario &&
      (reserva.data || dataReservaInput.value) === dataReservaInput.value,
  );
}

function buscarReserva(sala, horario) {
  return reservas.find(
    (reserva) =>
      reserva.sala === sala &&
      reserva.horario === horario &&
      (reserva.data || dataReservaInput.value) === dataReservaInput.value,
  );
}

function contarReservasPorSala(sala) {
  return filtrarReservasDoDia().filter((reserva) => reserva.sala === sala).length;
}

function renderizarGrafico() {
  const maximo = horariosValidos.length;

  ocupacaoChart.innerHTML = salasValidas
    .map((sala) => {
      const quantidade = contarReservasPorSala(sala);
      const porcentagem = Math.round((quantidade / maximo) * 100);

      return `
        <div class="chart-row">
          <div class="chart-label">
            <span>${sala}</span>
            <small>${quantidade}/${maximo} horarios</small>
          </div>
          <div class="chart-track">
            <div class="chart-bar" style="width: ${porcentagem}%"></div>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderizarNotificacoes() {
  const reservasDoDia = filtrarReservasDoDia();
  const mensagens = [];

  if (!reservasDoDia.length) {
    mensagens.push({
      titulo: "Dia livre",
      texto: "Todas as salas estao disponiveis na data selecionada.",
    });
  }

  const salasLotadas = salasValidas.filter(
    (sala) => contarReservasPorSala(sala) === horariosValidos.length,
  );

  salasLotadas.forEach((sala) => {
    mensagens.push({
      titulo: "Sala sem horarios livres",
      texto: `${sala} esta totalmente reservada neste dia.`,
    });
  });

  if (reservasDoDia.length) {
    mensagens.push({
      titulo: "Reservas ativas",
      texto: `${reservasDoDia.length} reserva(s) cadastrada(s) para ${formatarData(dataReservaInput.value)}.`,
    });
  }

  notificationList.innerHTML = mensagens
    .map(
      (mensagem) => `
        <article class="notification-item">
          <strong>${mensagem.titulo}</strong>
          <p>${mensagem.texto}</p>
        </article>
      `,
    )
    .join("");
}

function renderizarCalendario() {
  if (!calendarGrid) {
    return;
  }

  calendarGrid.style.gridTemplateColumns = `120px repeat(${salasValidas.length}, minmax(150px, 1fr))`;

  const cabecalho = [
    '<div class="calendar-cell calendar-header">Horario</div>',
    ...salasValidas.map(
      (sala) => `<div class="calendar-cell calendar-header">${sala}</div>`,
    ),
  ].join("");

  const linhas = horariosValidos
    .map((horario) => {
      const celulas = salasValidas
        .map((sala) => {
          const reserva = buscarReserva(sala, horario);

          if (reserva) {
            return `
              <div class="calendar-cell room-status">
                <span class="status-pill reserved">Reservada</span>
                <strong>${reserva.responsavel}</strong>
              </div>
            `;
          }

          return `
            <div class="calendar-cell room-status">
              <span class="status-pill available">Disponivel</span>
              <button
                class="reserve-from-calendar"
                type="button"
                data-sala="${sala}"
                data-horario="${horario}"
              >
                Reservar
              </button>
            </div>
          `;
        })
        .join("");

      return `<div class="calendar-cell time-cell">${horario}</div>${celulas}`;
    })
    .join("");

  calendarGrid.innerHTML = cabecalho + linhas;
}

async function criarReserva(dados) {
  if (existeConflito(dados.sala, dados.horario)) {
    mostrarMensagem("Esta sala ja esta ocupada neste horario.", "error");
    return;
  }

  if (usandoApi) {
    const resposta = await fetch(`${API_URL}/reservas`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    });

    if (!resposta.ok) {
      const erro = await resposta.json().catch(() => null);
      mostrarMensagem(erro?.detail || "Nao foi possivel reservar.", "error");
      return;
    }

    mostrarMensagem("Reserva confirmada na API.");
    await carregarReservas();
    return;
  }

  reservas.push({
    id: Date.now(),
    ...dados,
  });
  salvarDemo();
  renderizarReservas();
  mostrarMensagem("Reserva confirmada em modo demonstracao.");
}

async function cancelarReserva(id) {
  if (usandoApi) {
    await fetch(`${API_URL}/reservas/${id}`, { method: "DELETE" });
    await carregarReservas();
    return;
  }

  reservas = reservas.filter((reserva) => String(reserva.id) !== String(id));
  salvarDemo();
  renderizarReservas();
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const email = document.querySelector("#email").value.trim();
  const senha = document.querySelector("#senha").value.trim();

  if (email !== "professor@teste.com" || senha !== "123456") {
    alert("Use o login de demonstracao: professor@teste.com / 123456");
    return;
  }

  loginPanel.classList.add("hidden");
  dashboard.classList.remove("hidden");
  await carregarReservas();
});

reservationForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  await criarReserva({
    data: dataReservaInput.value,
    sala: salaSelect.value,
    horario: horarioSelect.value,
    responsavel: responsavelInput.value.trim(),
  });
});

reservasLista.addEventListener("click", async (event) => {
  const botao = event.target.closest("button[data-id]");

  if (!botao) {
    return;
  }

  await cancelarReserva(botao.dataset.id);
});

logoutButton.addEventListener("click", () => {
  dashboard.classList.add("hidden");
  loginPanel.classList.remove("hidden");
});

sidebarLogoutButton.addEventListener("click", () => {
  dashboard.classList.add("hidden");
  loginPanel.classList.remove("hidden");
});

dataReservaInput.addEventListener("change", () => {
  renderizarReservas();
});

previousDayButton.addEventListener("click", () => {
  const data = new Date(`${dataReservaInput.value}T12:00:00`);
  data.setDate(data.getDate() - 1);
  dataReservaInput.value = dataParaIso(data);
  renderizarReservas();
});

nextDayButton.addEventListener("click", () => {
  const data = new Date(`${dataReservaInput.value}T12:00:00`);
  data.setDate(data.getDate() + 1);
  dataReservaInput.value = dataParaIso(data);
  renderizarReservas();
});

calendarGrid.addEventListener("click", (event) => {
  const botao = event.target.closest("button[data-sala][data-horario]");

  if (!botao) {
    return;
  }

  salaSelect.value = botao.dataset.sala;
  horarioSelect.value = botao.dataset.horario;
  reservationForm.scrollIntoView({ behavior: "smooth", block: "center" });
  mostrarMensagem("Sala e horario selecionados pelo calendario.");
});

menuButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const section = document.querySelector(`#${button.dataset.target}`);

    if (!section) {
      return;
    }

    menuButtons.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    section.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

dataReservaInput.value = hojeFormatado();
preencherSelect(salaSelect, salasValidas);
preencherSelect(horarioSelect, horariosValidos);
