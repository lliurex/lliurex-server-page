xhttp = new XMLHttpRequest();
var resultado;
xhttp.onreadystatechange = function(){
    if(this.readyState == 4 && this.status == 200){
        let news = JSON.parse(this.responseText);
        if(news.length >= 1){
            if ( localStorage.getItem('lastnew') != news[0]['title'] || localStorage.getItem('readnews') == 'false' ){
                document.querySelector('#newsbutton').parentElement.querySelector('.notification').classList.add('visible');
            }
        }
        if (localStorage.getItem('lastnew') != news[0]['title']){
            localStorage.setItem('readnews',false);
        }
        localStorage.setItem('lastnew',news[0]['title']);
        news.forEach(element => {
            let n = document.createElement('a');
            n.href = element.link;
            n.innerHTML = element.title;
            n.title = element.summary;
            document.querySelector('#newslist').append(n);
        });
    }
};
xhttp.open("GET",urlfeed);
xhttp.send();


function setreadnews(){
    localStorage.setItem('readnews',true);
    document.querySelector('#newsbutton').parentElement.querySelector('.notification').classList.remove('visible');
}