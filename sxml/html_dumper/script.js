function onmessage(e) {
    drawInfo(e.data);
};

function sendMessage(msg) {
    Array.from(document.querySelectorAll('iframe')).forEach((e) => (
        e.contentWindow.postMessage(msg, '*')
    ));
}

function getOrCreate(id) {
    var elt = document.querySelector('#' + id);
    console.log(elt);
    if (elt === null) {
        elt = document.createElement('div');
        elt.id = id;
        document.body.insertBefore(elt, document.body.firstChild);
    }
    return elt;
}

function highlightElements(e) {
    Array.from(document.getElementsByClassName('sxml_active')).forEach((x) => {
        x.classList.remove('sxml_active');
    });
    e.target.classList.add('sxml_active');
    sendMessage(e.target.dataset.query);
}

function createTag(tag, cls, query) {
    var elt = document.createElement('span');
    elt.classList.add('sxml_tag');
    elt.classList.add(cls);
    elt.innerText = tag;
    elt.dataset.query = query || tag;
    elt.addEventListener('click', highlightElements);
    return elt;
}

function drawInfo(info) {
    var root = getOrCreate('sxml_info_root');
    root.innerHTML = '';
    info.forEach((e) => {
        var elt = document.createElement('div');
        console.log(e)
        root.append(elt);

        elt.append(createTag(e['tag'], 'tag'));
        if (e['id'] !== null) {
            elt.append(createTag(`#${e['id']}`, 'id'));
        }

        e['class'].forEach((className) => (
            elt.append(createTag(`.${className}`, 'class'))
        ));

        Object.entries(e['attributes']).forEach((attr) => {
            var tag = `${attr[0]}=${JSON.stringify(attr[1])}`;
            elt.append(createTag(
                tag, 'attr', `*[${tag}]`,
            ))
        });
    });
}

window.onload = function() {
    window.addEventListener('message', onmessage);
}
