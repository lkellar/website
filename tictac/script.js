function mark(button) {
    let letter = '';
    if (x) {
        letter = 'x';
    } else {
        letter = 'o';
    }
    const td = button.parentElement;
    button.remove();
    const letterImg = document.createElement('img');
    letterImg.src = `assets/${letter}.svg`;
    letterImg.className = letter;
    td.appendChild(letterImg);
    x = !x;
}

async function activate(button) {
    mark(button);
    if (await check()) {  clear(); return; }
    if (!multiplayer()) {
        await sleep(250);
        otherPlay();
        if (await check()) {
            clear();
        }
    }
}

function multiplayer() {
    return document.getElementById('multiplayer').checked;
}

let x = true;

matches = {1: [2,3,4], 2: [1,3,4], 3: [1,2,4], 4:[1,2,3]};

function clear() {
    Array.from(document.getElementsByTagName('img')).map(x => x.remove());
    Array.from(document.getElementsByTagName('button')).map(x => x.remove());
    for (const i of [1,2,3,4]) {
        const newButton = document.createElement('button');
        newButton.onclick = function () {activate(this)};
        document.getElementById(i.toString()).appendChild(newButton);
    }
    x = true;
}

async function check() {
    const buttons = Array.from(document.getElementsByTagName('img')).map(x => ({'id': Number(getID(x)), 'class': x.className}));
    const x = [];
    const y = [];
    for (const i of buttons) {
        if (i.class === 'x') {
            x.push(i.id);
        } else if (i.class === 'y') {
            y.push(i.id);
        }
    }
    for (const listo of [x, y]) {
        for (const i of listo) {
            for (const m of matches[i]) {
                if (m in listo) {
                    if (listo === x) {
                        await win('x');
                    } else {
                        await win('y');
                    }
                    return true
                }
            }
        }
    }
    return false
}

function getID(ele) {
    return ele.parentElement.id;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function getRandomInt(max) {
    return Math.floor(Math.random() * Math.floor(max));
}

function otherPlay() {
    const buttons = document.getElementsByTagName('button');
    mark(buttons[getRandomInt(buttons.length)])
}

async function win(letter) {
    const letters = document.getElementsByClassName(letter);
    await sleep(250);
    for (const i of letters) {
        i.src = `assets/${letter}Win.svg`
    }
    await sleep(250);
    for (const i of letters) {
        i.src = `assets/${letter}.svg`
    }
    await sleep(250);
    for (const i of letters) {
        i.src = `assets/${letter}Win.svg`
    }
    await sleep(500);
}