function getCookie(key) {
    if (!key) return null;

    const cookieReg = new RegExp(`(^|;\\s*)${key}=([^;]+)`);
    const match = document.cookie.match(cookieReg);
    return match ? decodeURIComponent(match[2]) : null;
}

function gotoRoom(roomId) {
    window.location.href = `room?roomId=${roomId}`;
}

function gotoLogin() {
    window.location.href = 'login';
}

function gotoLobby() {
    window.location.href = 'lobby';
}

function getUserFromCookie() {
    return getCookie("user")
}

function clearAllCookies() {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i];
        const eqPos = cookie.indexOf("=");
        const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
    }
    localStorage.clear()
}

function checkLoginOrGotoLoginPage(apiResponse) {
    if (apiResponse.reLogin) {
        clearAllCookies();
        gotoLogin();
    }
}

function showToastAndFadeout(toastElement) {
    showToast(toastElement);

    setTimeout(() => {
        fadeOutToast(toastElement);
    }, 1200);
}

function showToast(toastElement) {
    toastElement.style.opacity = '0';
    toastElement.style.display = 'block';
    void toastElement.offsetWidth;
    toastElement.style.opacity = '1';
}

function fadeOutToast(toastElement) {
    toastElement.style.opacity = '0';
    setTimeout(() => {
        toastElement.style.display = 'none';
    }, 500);
}
