
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
    var info_json = {};

    // title
    if (/^\/question/.test(window.location.pathname)) {
        var title = document.getElementById("zh-question-title").
                childNodes[1].textContent;
        info_json["name"] = title.trim();
    } else if (/^\/people/.test(window.location.pathname)) {
        var name = document.getElementsByClassName("name")[0].textContent;
        info_json["name"] = name.trim();
    }

    return JSON.stringify(info_json);
}

function follow(follow_type) {
    var follow, match;
    if (follow_type === "question") {
        match = window.location.pathname.match(/^(\/question\/\d+)/);
        follow = match[1];
    } else if (follow_type === "people") {
        match = window.location.pathname.match(/^(\/people\/[a-zA-Z0-9_-]+)/);
        follow = match[1];
    }
    // console.log(follow);
    // to pass django csrf check, both credentials(cookie)
    // and X-CSRFToken are needed
    window.fetch(follow, {
        method:'POST',
        credentials:'same-origin',
        body:followInfo(),
        headers:{"Content-Type":"application/json",
                 "X-CSRFToken":getCookie("csrftoken")}
    }).then(function(resp) {
        if (resp.status==200) alert("success");
    });
}

// only available at index page
function unfollow(elemId) {
    var pathname = document.getElementById(elemId).
            getElementsByTagName('a')[0].pathname;
    window.fetch(pathname, {
        method:'DELETE',
        credentials:'same-origin',
        // body:unfollowInfo(elemId),
        headers:{"Content-Type":"application/json",
                 "X-CSRFToken":getCookie("csrftoken")}
    }).then(function(resp) {
        if (resp.status==200) {
            var li = document.getElementById(elemId);
            li.parentNode.removeChild(li);
        }
    });
}
