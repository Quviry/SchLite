
/*═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
 ═ Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.                                       ═
 ═ Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.                        ═
 ═ Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.                                                   ═
 ═ Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.                     ═
 ═ Vestibulum commodo. Ut rhoncus gravida arcu.                                                                       ═
 ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════*/

function crypt_sha256(s){
 var chrsz = 8;
 var hexcase = 0;

 function safe_add (x, y) {
 var lsw = (x & 0xFFFF) + (y & 0xFFFF);
 var msw = (x >> 16) + (y >> 16) + (lsw >> 16);
 return (msw << 16) | (lsw & 0xFFFF);
 }

 function S (X, n) { return ( X >>> n ) | (X << (32 - n)); }
 function R (X, n) { return ( X >>> n ); }
 function Ch(x, y, z) { return ((x & y) ^ ((~x) & z)); }
 function Maj(x, y, z) { return ((x & y) ^ (x & z) ^ (y & z)); }
 function Sigma0256(x) { return (S(x, 2) ^ S(x, 13) ^ S(x, 22)); }
 function Sigma1256(x) { return (S(x, 6) ^ S(x, 11) ^ S(x, 25)); }
 function Gamma0256(x) { return (S(x, 7) ^ S(x, 18) ^ R(x, 3)); }
 function Gamma1256(x) { return (S(x, 17) ^ S(x, 19) ^ R(x, 10)); }

 function core_sha256 (m, l) {
 var K = new Array(0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5, 0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174, 0xE49B69C1, 0xEFBE4786, 0xFC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA, 0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x6CA6351, 0x14292967, 0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85, 0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070, 0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3, 0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2);
 var HASH = new Array(0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19);
 var W = new Array(64);
 var a, b, c, d, e, f, g, h, i, j;
 var T1, T2;

 m[l >> 5] |= 0x80 << (24 - l % 32);
 m[((l + 64 >> 9) << 4) + 15] = l;

 for ( var i = 0; i<m.length; i+=16 ) {
 a = HASH[0];
 b = HASH[1];
 c = HASH[2];
 d = HASH[3];
 e = HASH[4];
 f = HASH[5];
 g = HASH[6];
 h = HASH[7];

 for ( var j = 0; j<64; j++) {
 if (j < 16) W[j] = m[j + i];
 else W[j] = safe_add(safe_add(safe_add(Gamma1256(W[j - 2]), W[j - 7]), Gamma0256(W[j - 15])), W[j - 16]);

 T1 = safe_add(safe_add(safe_add(safe_add(h, Sigma1256(e)), Ch(e, f, g)), K[j]), W[j]);
 T2 = safe_add(Sigma0256(a), Maj(a, b, c));

 h = g;
 g = f;
 f = e;
 e = safe_add(d, T1);
 d = c;
 c = b;
 b = a;
 a = safe_add(T1, T2);
 }

 HASH[0] = safe_add(a, HASH[0]);
 HASH[1] = safe_add(b, HASH[1]);
 HASH[2] = safe_add(c, HASH[2]);
 HASH[3] = safe_add(d, HASH[3]);
 HASH[4] = safe_add(e, HASH[4]);
 HASH[5] = safe_add(f, HASH[5]);
 HASH[6] = safe_add(g, HASH[6]);
 HASH[7] = safe_add(h, HASH[7]);
 }
 return HASH;
 }

 function str2binb (str) {
 var bin = Array();
 var mask = (1 << chrsz) - 1;
 for(var i = 0; i < str.length * chrsz; i += chrsz) {
 bin[i>>5] |= (str.charCodeAt(i / chrsz) & mask) << (24 - i % 32);
 }
 return bin;
 }

 function Utf8Encode(string) {
 string = string.replace(/\r\n/g,'\n');
 var utftext = '';

 for (var n = 0; n < string.length; n++) {

 var c = string.charCodeAt(n);

 if (c < 128) {
 utftext += String.fromCharCode(c);
 }
 else if((c > 127) && (c < 2048)) {
 utftext += String.fromCharCode((c >> 6) | 192);
 utftext += String.fromCharCode((c & 63) | 128);
 }
 else {
 utftext += String.fromCharCode((c >> 12) | 224);
 utftext += String.fromCharCode(((c >> 6) & 63) | 128);
 utftext += String.fromCharCode((c & 63) | 128);
 }

 }

 return utftext;
 }

 function binb2hex (binarray) {
 var hex_tab = hexcase ? '0123456789ABCDEF' : '0123456789abcdef';
 var str = '';
 for(var i = 0; i < binarray.length * 4; i++) {
 str += hex_tab.charAt((binarray[i>>2] >> ((3 - i % 4)*8+4)) & 0xF) +
 hex_tab.charAt((binarray[i>>2] >> ((3 - i % 4)*8 )) & 0xF);
 }
 return str;
 }

 s = Utf8Encode(s);
 return binb2hex(core_sha256(str2binb(s), s.length * chrsz));
};

function getCookie(name) {
  var cookies = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return cookies ? decodeURIComponent(cookies[1]) : undefined;
};

let notify = async function notify(str) {
    const notification_bucket = document.getElementById('notifications')
    const next_child = document.createElement('div')
    next_child.classList.add('notification');
    next_child.classList.add('error');
    next_child.innerHTML = str;
    notification_bucket.appendChild(next_child);
    setTimeout(function(){notification_bucket.removeChild(next_child);}, 5000);
};

if (!String.prototype.trim) {
  (function() {
    // Вырезаем BOM и неразрывный пробел
    String.prototype.trim = function() {
      return this.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g, '');
    };
  })();
};

function contains(arr, elem) {
    for (var i = 0; i < arr.length; i++) {
        if (arr[i].toString() === elem.toString()) {
            return true;
        }
    }
    return false;
};

/**
 *
 * @param day {Date}
 */
function get_day_unique(day){
    return (day.getDate() + day.getMonth()*31 + day.getFullYear()*365);
}

APP_STATE = {};

function load_and_execute(url, exec){
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.code === 200){
                exec(data.content);
            }else{
                notify(data.errors);
            }
        }).catch(()=>{
                notify('Error while loading');
            }
        )
};


/**
 *@param data {Object}
 *@param name {string}
 */
function register_to_local_storage(data, name) {
    const local_storage = window.localStorage;
    local_storage.setItem(name, JSON.stringify(data));
    return data;
};

function send_done_to_server(done){
    let data = {
        'method': 'POST',
        'body': JSON.stringify(done),
        'mode': 'same-origin',
        'headers': {
            "X-CSRFToken": getCookie("csrftoken")
        }

    }
    fetch('/api_set_done/', data).then(null).catch((data) => notify('Server responded with response_code'+ data))
};

/**
 * @param {string} id
 */
function check_done(id) {
    const local_storage = window.localStorage;
    let done_list = JSON.parse(local_storage.getItem('done_list')) || [];
    done_list.push([new Date().toISOString().slice(0, 10), id])
    send_done_to_server(done_list)
    local_storage.setItem('done_list', JSON.stringify(done_list));
    document.getElementById(id).style.display = 'none';
};

/**
 * @param {string} id
 */
function is_done(id) {
    const local_storage = window.localStorage;
    let done_list = JSON.parse(local_storage.getItem('done_list')) || [];
    for(let note of done_list){
        if (note[1] == id){
            return true
        }
    }
    return false
};

/**
 * @param {string} homework
 * @param {string} lesson
 * @param {Date} day
 */
function createLesson(homework, lesson, day){
    let lesson_container = document.createElement('div');
    let lesson_info_container = document.createElement('div');
    let lesson_homework = document.createElement('div');
    let lesson_class = document.createElement('div');

    lesson_container.classList.add('lesson_container');
    lesson_info_container.classList.add('lesson_top_info');
    lesson_homework.classList.add('lesson_homework');
    lesson_class.classList.add('lesson_class');
    lesson_class.innerHTML = lesson;
    lesson_homework.innerHTML =  homework;
    lesson_info_container.appendChild(lesson_class);

    lesson_container.id = crypt_sha256(day.toDateString()+ lesson + homework);


    let today = new Date();
    if (day.getDate() === today.getDate()){
        let daymark = document.createElement('div');
        daymark.classList.add('day_mark__today');
        daymark.innerText = 'СЕГОДНЯ';
        lesson_info_container.appendChild(daymark);
    }else if(day.getDate() === new Date(today.setDate(today.getDate()+1)).getDate()){
        let daymark = document.createElement('div');
        daymark.classList.add('day_mark__tomorrow');
        daymark.innerText = 'ЗАВТРА';
        lesson_info_container.appendChild(daymark);
    }
    let check_button = document.createElement('a');
    check_button.classList.add('check_button');
    check_button.addEventListener('click', () => { check_done(lesson_container.id);} );
    let check_button_icon = document.createElement('img');
    check_button_icon.classList.add('check_button__icon');
    check_button_icon.src = 'static/images/done.svg';
    check_button_icon.alt = 'Done icon';
    check_button_icon.height = '14';
    check_button_icon.width = '14';
    check_button.appendChild(check_button_icon);
    lesson_info_container.appendChild(check_button);

    lesson_container.appendChild(lesson_info_container);
    lesson_container.appendChild(lesson_homework);

    if(is_done(lesson_container.id)) {
        lesson_container.style.display = 'none';
        document.getElementById('schedule').prepend(lesson_container);
        return null;
    }
    return lesson_container;
};

/**
 *
 * @param api_data {jsonFormat}
 */
function update_schedule(api_data){
    const local_timetable = register_to_local_storage(api_data['timetable'], 'api_timetable');
    const local_homework = register_to_local_storage(api_data['homework'], 'api_homework');
    const schedule_container = document.getElementById('schedule');
    schedule_container.innerText = '';
    const now = new Date;
    for(let day of local_homework){
        let day_container = document.createElement('div');
        let day_header = document.createElement('h3');
        let day_containment = document.createElement('div');
        day_container.classList.add('day_container');
        day_header.classList.add('day_header');
        day_containment.classList.add('day_containment');
        for(let date in day) {
            let _day = new Date(date);
            day_header.innerHTML = _day.toLocaleString('ru',
                {month: 'long', day: 'numeric', weekday: 'long'})
                .replace(/(^|\s)\S/g, l => l.toUpperCase())
            for(let lesson in day[date]){
                let homework = day[date][lesson]['homework'];
                let subject = day[date][lesson]['lesson'];
                let lesson_box = createLesson(homework, subject, _day);
                if (lesson_box != null){
                    day_containment.appendChild(lesson_box);
                }
            }
        }
        if(day_containment.children.length !== 0){
                day_container.appendChild(day_header);
                day_container.appendChild(day_containment);
                schedule_container.appendChild(day_container);
        }
    }
    schedule_container.classList.add('active');
};


function update_done(data) {
    const local_storage = window.localStorage;
    let done_list = JSON.parse(local_storage.getItem('done_list')) || [];
    for (let done_note of data){
        if( !contains(done_list, done_note)){
            done_list.push(done_note);
        }
    }
    local_storage.setItem('done_list', JSON.stringify(done_list));
};

function update_backpack(data) {
    register_to_local_storage(data, 'api_backpack');
    let timetable = JSON.parse(localStorage.getItem('api_timetable'));
    let backpack_list = document.createElement('div');
    backpack_list.classList.add('backpack_list');
    for(let order in data){
        let backpack_item = document.createElement('div');
        backpack_item.classList.add('backpack_item');
        let time_container = document.createElement('div');
        backpack_item.classList.add('time_container');
        let lesson = document.createElement('div');
        time_container.innerText = timetable[order - 1];
        lesson.innerText = data[order];
        backpack_item.appendChild(lesson);
        backpack_item.appendChild(time_container);
        backpack_list.appendChild(backpack_item);
    }
    document.getElementById('webapp').appendChild(backpack_list);
};

function switch_done_show() {
    let schedule = document.getElementById('schedule');
    if (!schedule.classList.contains('active')){
        schedule.classList.add('active');
        let done_container = document.getElementById('done_container');
        done_container.classList.remove('active');
        done_container.id = 'done_removing_container';
        setTimeout(() => {done_container.remove()}, 2000);
    }else{
        let done_container = document.createElement('div');
        done_container.id = 'done_container';
        let done_container_top = document.createElement('h3');
        done_container_top.id = 'done_container_top';
        done_container_top.innerText = 'Сделано:'
        done_container.appendChild(done_container_top);
        for(let el of document.getElementsByClassName('lesson_container')){
            if(el.style.display === 'none'){
                let elc = el.cloneNode(true);
                elc.style.display = 'block';
                done_container.appendChild(elc);
            }
        }
        document.getElementById('webapp').appendChild(done_container);
        schedule.classList.remove('active');
        done_container.classList.add('active');
    }
};

function setup_bot_buttons() {
    let backpack_button = document.getElementById('backpack__button');
    let done_button = document.getElementById('done__button');
    done_button.addEventListener('click', switch_done_show)
}
function load_schedule() {
        load_and_execute('/api_schedule/', update_schedule)
    }
function load_done() {
        load_and_execute('/api_get_done/', update_done)
    };

function load_backpack() {
        load_and_execute('/api_get_backpack/', update_backpack)
    }

function load_api_data() {
        load_schedule();
        load_done();
        load_backpack();
}

async function set_updating_timer(){
    let data = new Date();
    setInterval(() => {
        if(get_day_unique(data) !== get_day_unique(new Date())){
            load_api_data(); // TODO optimise
            data = new Date();
        }
    }, 1000);
};

function raise_worker(){
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(function (response) {
                // Service worker registration done
                console.log('Registration Successful', response);
            }, function (error) {
                // Service worker registration failed
                notify('Offline work unsupported');
                console.log('Registration Failed', error);
            })
    }else{
        notify('Offline work unsupported in this browser');
    }
};

window.addEventListener('load', ()=> {
    // TODO today-list
    raise_worker();
    load_api_data();
    set_updating_timer().catch();
    setup_bot_buttons();
});
