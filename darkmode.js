function triggerDarkMode(on) {
    if (on) {
        changeSpanText(true);
        localStorage.setItem('darkmode', 'true');
    } else {
        changeSpanText(false);
        localStorage.setItem('darkmode', 'false');
    }
    document.body.classList.toggle('darkmode');
}

function toggle() {
    const darkValue = localStorage.getItem('darkmode');
    if (darkValue === 'true') {
      triggerDarkMode(false);
    } else {
        triggerDarkMode(true);
    }
}

function changeSpanText(on) {
    const ele = document.getElementById('darkmode');
    if (ele) {
        if (on) {
            ele.getElementsByTagName('h1')[0].textContent = 'Deactivate Dark Mode';
            ele.getElementsByTagName('button')[0].textContent = 'Deactivate';
            ele.getElementsByTagName('p')[0].textContent = 'A nifty way to deactivate dark mode';
        } else {
            ele.getElementsByTagName('h1')[0].textContent = 'Activate Dark Mode';
            ele.getElementsByTagName('button')[0].textContent = 'Activate';
            ele.getElementsByTagName('p')[0].textContent = 'A nifty way to activate dark mode';
        }
    }
}

function darkTest(e) {
    if (e.matches) {
        triggerDarkMode(true);
    } else {
        triggerDarkMode(false);
    }
}

function init() {
    const darkValue = localStorage.getItem('darkmode');
    const mql = window.matchMedia('(prefers-color-scheme: dark)');
    mql.addListener(darkTest);
    if (darkValue === 'true' || mql.matches) {
        triggerDarkMode(true);
    }
}

init();