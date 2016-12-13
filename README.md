Trabalho para a disciplina de Algoritmos Evolutivos.


O código tá feio, semana que vem eu arrumo.


Antes de rodar:

-> Crie um .txt contendo os atalhos da sua pasta de músicas.

-->ls -R > musicas.txt

-->As músicas devem estar em pastas, com apenas um diretório de profundidade. (depois eu faço algo mais genérico)

-->Retire o cabeçalho de pastas

-->Formatação:

./Bored Generation:

NOFX - Drugs Are Good.mp3


./Born on the Blues:

B.B. King - The Thrill Is Gone.mp3


./Bounce:

Bon Jovi - Everyday.mp3

Bon Jovi - Misunderstood.mp3


./Bravo Black Hits, Volume 29:

Stromae - papaoutai.mp3


./Bravo Black Hits, Volume 5:

Nelly - Ride Wit Me.mp3


-> Utilize o analyser.py para criar um relatório das suas musicas

-->python analyser.py <relatorio>

-->Ele pega os metadados das musicas e organiza de forma legível ao player.

-->Leva em torno de 7 a 8 segundos por musica, devido a analise de bpm


->Rode

-->python player.py report.txt



Comandos:

p -> pausa

s -> status do player

f -> musicas no frame

n -> proxima musica

l -> trava o teclado (ctrl+c destrava no linux. não use no windows, foi feito pra testes, eu vou tirar isso depois.)
