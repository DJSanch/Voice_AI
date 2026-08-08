const $ = (selector) => document.querySelector(selector);
const stateUrl = '/api/state';
const devicesUrl = '/data/network_devices.json';
const securityUrl = '/data/security_events.json';

function setText(selector, value) { $(selector).textContent = value; }
function titleCase(value) { return value ? value.replace(/\b\w/g, (letter) => letter.toUpperCase()) : 'Offline'; }

function renderConversation(lastResponse, liveResponse) {
  const container = $('#conversation-history');
  const message = document.createElement('div');
  const label = document.createElement('span');
  const text = document.createElement('p');
  message.className = 'message astra';
  label.textContent = liveResponse ? 'Astra · live update' : 'Astra · most recent reply';
  text.textContent = liveResponse || lastResponse || 'I’m ready when you are.';
  message.append(label, text);
  container.replaceChildren(message);
}

function updateClock() {
  const now = new Date();
  setText('#clock', now.toLocaleString([], { weekday: 'short', hour: '2-digit', minute: '2-digit' }));
  setText('#daypart', now.getHours() < 12 ? 'morning' : now.getHours() < 18 ? 'afternoon' : 'evening');
}

async function loadState() {
  try {
    const response = await fetch(`${stateUrl}?t=${Date.now()}`, { cache: 'no-store' });
    if (!response.ok) throw new Error('State unavailable');
    const state = await response.json();
    const online = state.status && state.status !== 'offline';
    setText('#status', titleCase(state.status));
    setText('#activity', state.activity || 'Astra is standing by.');
    renderConversation(state.last_response, state.live_response);
    setText('#voice-mode', online ? titleCase(state.status) : 'Standing by');
    setText('#voice-health', online ? 'Active' : 'Waiting');
    setText('#updated', state.updated_at ? `Last update ${new Date(state.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : 'Astra has not published an update yet.');
    $('#connection-dot').parentElement.classList.toggle('offline', !online);
    setText('#connection-label', online ? 'LOCAL CONNECTED' : 'LOCAL OFFLINE');
  } catch (_) {
    $('#connection-dot').parentElement.classList.add('offline');
    setText('#connection-label', 'LOCAL OFFLINE');
  }
}

async function loadDevices() {
  try {
    const response = await fetch(devicesUrl, { cache: 'no-store' });
    if (!response.ok) throw new Error('Device data unavailable');
    const devices = await response.json();
    setText('#network-count', `${devices.length} devices`);
    setText('#device-total', devices.length);
    const list = $('#device-list');
    list.replaceChildren(...devices.slice(0, 4).map((device) => {
      const item = document.createElement('li');
      const identity = document.createElement('span');
      const name = document.createElement('strong');
      const detail = document.createElement('small');
      const type = document.createElement('span');
      name.textContent = device.hostname || 'Unknown device';
      detail.textContent = device.vendor || device.ip || 'Local network';
      type.className = 'device-type';
      type.textContent = device.type || 'DEVICE';
      identity.append(name, detail);
      item.append(identity, type);
      return item;
    }));
  } catch (_) { setText('#network-health', 'Unavailable'); }
}

async function loadSecurity() {
  try {
    const response = await fetch(securityUrl, { cache: 'no-store' });
    const events = response.ok ? await response.json() : [];
    setText('#security-status', events.length ? `${events.length} alert${events.length === 1 ? '' : 's'}` : 'No alerts');
    setText('#security-health', events.length ? 'Attention' : 'Ready');
  } catch (_) { setText('#security-health', 'Unavailable'); }
}

document.querySelectorAll('[data-command]').forEach((button) => button.addEventListener('click', async () => {
  const phrase = button.dataset.command;
  button.disabled = true;
  try {
    const response = await fetch('/api/commands', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: phrase }),
    });
    if (!response.ok) throw new Error('Command rejected');
    setText('#command-hint', `Sent to Astra: “${phrase}”`);
    loadState();
  } catch (_) {
    setText('#command-hint', 'Could not reach Astra. Start the voice assistant, then open http://localhost:8080.');
  } finally { button.disabled = false; }
}));

updateClock(); loadState(); loadDevices(); loadSecurity();
setInterval(updateClock, 30_000); setInterval(loadState, 1_000); setInterval(loadDevices, 30_000); setInterval(loadSecurity, 30_000);
