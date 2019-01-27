function setCookie(name, value) {
    document.cookie = name + '=' + value  + '; path=/';
}

function getCookie(c_name) {
    let c_start;
    let c_end;
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + '=');
        if (c_start !== -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(';', c_start);
            if (c_end === -1) {
                c_end = document.cookie.length;
            }
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return null;
}

function triggerDarkMode(on) {
    if (on) {
        changeSpanText(true);
        setCookie('darkmode', 'true');
    } else {
        changeSpanText(false);
        setCookie('darkmode', 'false');
    }
    document.body.classList.toggle('darkmode');
}

function toggle() {
    const cookie = getCookie('darkmode');
    if (cookie === 'true') {
      triggerDarkMode(false);
    } else {
        triggerDarkMode(true);
    }
}

function changeSpanText(on) {
    const ele = document.getElementById('darkmode');
    console.log(ele);
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
    const cookie = getCookie('darkmode');
    const mql = window.matchMedia('(prefers-color-scheme: dark)');
    mql.addListener(darkTest);
    if (cookie === 'true' || mql.matches) {
        triggerDarkMode(true);
    }
}

init();