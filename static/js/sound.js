let musicEnabled =
    localStorage.getItem("musicEnabled") !== "false";

let soundEnabled =
    localStorage.getItem("soundEnabled") !== "false";

document.addEventListener("DOMContentLoaded", function () {

    const music =
        document.getElementById("bgMusic");

    const musicBtn =
        document.getElementById("musicBtn");

    const soundBtn =
        document.getElementById("soundBtn");

    if (musicBtn) {

        musicBtn.innerHTML =
            musicEnabled
                ? "🎵 Music ON"
                : "🔇 Music OFF";

    }

    if (soundBtn) {

        soundBtn.innerHTML =
            soundEnabled
                ? "🔊 Sound ON"
                : "🔇 Sound OFF";

    }

    if (music) {

        music.volume = 0.3;

        const shouldPlay =
            localStorage.getItem("musicEnabled")
            !== "false";

        if (shouldPlay) {

            music.play()
                .catch(() => { });

        }

    }

});

function toggleMusic() {

    const music =
        document.getElementById("bgMusic");

    const btn =
        document.getElementById("musicBtn");

    musicEnabled = !musicEnabled;

    localStorage.setItem(
        "musicEnabled",
        musicEnabled
    );

    if (music) {

        if (musicEnabled) {

            music.play();

        } else {

            music.pause();

        }

    }

    if (btn) {

        btn.innerHTML =
            musicEnabled
                ? "🎵 Music ON"
                : "🔇 Music OFF";

    }

}

function toggleSound() {

    soundEnabled = !soundEnabled;

    localStorage.setItem(
        "soundEnabled",
        soundEnabled
    );

    const btn =
        document.getElementById("soundBtn");

    if (btn) {

        btn.innerHTML =
            soundEnabled
                ? "🔊 Sound ON"
                : "🔇 Sound OFF";

    }

}

function playClick() {

    if (!soundEnabled)
        return;

    const click =
        document.getElementById("clickSound");

    if (click) {

        click.currentTime = 0;

        click.play();

    }

}