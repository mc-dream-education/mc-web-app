// Globale Variablen innerhalb des Moduls
let state = {
    fullText: "",
    filename: "",
    pastErrors: [],
    currentIndex: 0,
    currentWordIndex: 0,
    mode: 'all',
    words: []
};

const neighbors = {
    'q':['w','a'], 'w':['q','e','a','s'], 'e':['w','r','s','d'], 'r':['e','t','d','f'], 't':['r','z','f','g'],
    'z':['t','u','g','h'], 'u':['z','i','h','j'], 'i':['u','o','j','k'], 'o':['i','p','k','l'], 'p':['o','l','ö'],
    'a':['q','w','s','y'], 's':['a','w','e','d','x','y'], 'd':['s','e','r','f','c','x'], 'f':['d','r','t','g','v','c'],
    'g':['f','t','z','h','b','v'], 'h':['g','z','u','j','n','b'], 'j':['h','u','i','k','m','n'], 'k':['j','i','o','l','m'],
    'l':['k','o','p','ö'], 'y':['a','s','x'], 'x':['y','s','d','c'], 'c':['x','d','f','v'], 'v':['c','f','g','b'],
    'b':['v','g','h','n'], 'n':['b','h','j','m'], 'm':['n','j','k']
};

// Diese Funktion wird vom HTML aus aufgerufen
function initExercise(config) {
    state.fullText = config.fullText;
    state.filename = config.filename;
    state.pastErrors = config.pastErrors;
    state.words = config.fullText.split(' ');

    renderText();
    createKeyboard();
    setupPhysicalKeyboard();
}

function renderText() {
    const container = document.getElementById('text-container');
    container.innerHTML = state.words.map((w, wIdx) => {
        const isPastError = state.pastErrors.includes(w.replace(/[.,!?;:]/g, '')) ? 'past-error' : '';
        const chars = w.split('').map((c, cIdx) => `<span class="char" id="c-${wIdx}-${cIdx}">${c}</span>`).join('');
        return `<span class="word ${isPastError}" id="w-${wIdx}">${chars}</span>`;
    }).join(' ');
    updateHighlight();
}

function handleInput(key) {
    key = key.toLowerCase();
    let currentWord = state.words[state.currentWordIndex];
    let targetChar = currentWord[state.currentIndex].toLowerCase();

    if (key === targetChar) {
        if (state.mode === 'first') {
            finishWord();
        } else {
            markCorrect();
        }
    } else if (neighbors[targetChar] && neighbors[targetChar].includes(key)) {
        triggerFatFinger();
    } else {
        logError(currentWord);
    }
}

function finishWord() {
    let currentWord = state.words[state.currentWordIndex];
    for (let i = state.currentIndex; i < currentWord.length; i++) {
        const charEl = document.getElementById(`c-${state.currentWordIndex}-${i}`);
        if (charEl) charEl.classList.add('correct');
    }
    moveToNextWord();
}

function markCorrect() {
    document.getElementById(`c-${state.currentWordIndex}-${state.currentIndex}`).classList.add('correct');
    state.currentIndex++;

    while (state.currentIndex < state.words[state.currentWordIndex].length &&
           /[^a-zA-Z0-9äöüÄÖÜ]/.test(state.words[state.currentWordIndex][state.currentIndex])) {
        document.getElementById(`c-${state.currentWordIndex}-${state.currentIndex}`).classList.add('correct');
        state.currentIndex++;
    }

    if (state.currentIndex >= state.words[state.currentWordIndex].length) {
        moveToNextWord();
    }
    updateHighlight();
}

function moveToNextWord() {
    state.currentIndex = 0;
    state.currentWordIndex++;
    if (state.currentWordIndex >= state.words.length) {
        alert("Hervorragend! Du hast den Text abgeschlossen.");
    } else {
        const nextWord = document.getElementById(`w-${state.currentWordIndex}`);
        nextWord.scrollIntoView({ behavior: 'smooth', block: 'center' });
        updateHighlight();
    }
}

function logError(word) {
    const wordEl = document.getElementById(`w-${state.currentWordIndex}`);
    wordEl.classList.add('wrong');
    setTimeout(() => wordEl.classList.remove('wrong'), 500);

    fetch('/log_error', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ filename: state.filename, word: word.replace(/[.,!?;:]/g, '') })
    });
}

function triggerFatFinger() {
    const container = document.getElementById('text-container');
    container.classList.add('fat-finger-warn');
    setTimeout(() => container.classList.remove('fat-finger-warn'), 300);
}

function updateHighlight() {
    document.querySelectorAll('.char.current').forEach(el => el.classList.remove('current'));
    const active = document.getElementById(`c-${state.currentWordIndex}-${state.currentIndex}`);
    if (active) active.classList.add('current');
}

function toggleHelp() {
    document.getElementById('text-container').classList.toggle('hidden-text');
}

function setMode(m) {
    state.mode = m;
    state.currentIndex = 0;
    state.currentWordIndex = 0;
    renderText();
}

function setupPhysicalKeyboard() {
    // Entferne alte Listener, falls vorhanden, um Duplikate zu vermeiden
    window.removeEventListener('keydown', window._keyHandler);
    window._keyHandler = (e) => {
        if (e.key.length === 1) handleInput(e.key);
    };
    window.addEventListener('keydown', window._keyHandler);
}

function createKeyboard() {
    const layout = ["qwertzuiopü", "asdfghjklöä", "yxcvbnm"];
    const kb = document.getElementById('virtual-keyboard');
    kb.innerHTML = '';
    layout.forEach(row => {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'kb-row';
        row.split('').forEach(key => {
            const btn = document.createElement('button');
            btn.innerText = key.toUpperCase();
            btn.onclick = () => handleInput(key);
            rowDiv.appendChild(btn);
        });
        kb.appendChild(rowDiv);
    });
}

function toggleHelp() {
    const container = document.getElementById('text-container');
    const btn = document.getElementById('btn-help-toggle');

    // Toggle der Klasse für den Text (ausgeblendet oder nicht)
    const isHidden = container.classList.toggle('hidden-text');

    if (isHidden) {
        // Hilfstext ist jetzt VERSTECKT
        btn.innerText = "Hilfstext Einblenden";
        btn.classList.remove('btn-on');
        btn.classList.add('btn-off');
    } else {
        // Hilfstext ist jetzt SICHTBAR
        btn.innerText = "Hilfstext Ausblenden";
        btn.classList.remove('btn-off');
        btn.classList.add('btn-on');
    }
}