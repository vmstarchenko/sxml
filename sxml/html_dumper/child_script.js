function elementInfo(e) {
    var info = [];
    for (; e.parentElement != null && e.tagName != 'BODY'; e=e.parentElement) {
        var attrs = Object.fromEntries(Array.from(e.attributes).map((e) => ([e.name, e.value])));
        delete attrs['id'];
        delete attrs['class'];
        var curInfo = {
            'id': e.id || null,
            'tag': e.tagName,
            'class': [...e.classList].filter((e) => (e != hl_class)),
            'attributes': attrs,
        };
        info.push(curInfo);
    }
    return info;
}

function onclick(e) {
    window.top.postMessage(elementInfo(e.target), '*');
    return false;
}

window.onload = function() {
    Array.from(document.getElementsByTagName("a")).forEach(function(e) {
        e.onclick = function() {return false;}
    });

    document.querySelector('html').addEventListener("click", onclick);
}

var hl_class = '__sxml_highlight';
window.onmessage = function(e) {
    Array.from(document.getElementsByClassName(hl_class)).forEach((e) => {
        e.classList.remove(hl_class);
    });
    Array.from(document.querySelectorAll(e.data)).forEach((e) => {
        e.classList.add(hl_class);
    });
};
