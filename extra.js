function generateRandomResponse() {
    const alphabet = "ABC"  
    return alphabet[Math.floor(Math.random() * alphabet.length)]
}

let $dice = document.querySelector('.dice-pic');
let $diceresp = document.querySelector('.dice-resp');

$dice.addEventListener( 'click', function(){
  $diceresp.innerHTML = generateRandomResponse();  
});