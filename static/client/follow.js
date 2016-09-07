
// https://docs.djangoproject.com/en/1.10/ref/csrf/#ajax
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue =
                    decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function followInfo() {
    var info_arr = window.location.pathname.split('/').filter(function(x) {
        return x !== (undefined || '');
    });
    var info_json = {};
    for (var i = 0; i < info_arr.length; i+=2) {
        info_json[info_arr[i]] = info_arr[i+1];
    }

    // title
    var title = document.getElementById("zh-question-title").
            childNodes[1].textContent;
    info_json["title"] = title.trim();

    return JSON.stringify(info_json);
}

function follow(){
    // to pass django csrf check, both credentials(cookie)
    // and X-CSRFToken are needed
    fetch('/follow', {
        method:'POST',
        credentials:'same-origin',
        body:followInfo(),
        headers:{"Content-Type":"application/json",
                 "X-CSRFToken":getCookie("csrftoken")}
    }).then(function(resp) {
        if (resp.status==200) alert("success");
    });
}
