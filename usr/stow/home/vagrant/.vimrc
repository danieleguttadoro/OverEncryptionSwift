" scriviamo le modifiche prima di cambiare buffer
set autowrite

" il nostro terminale ha una palette di colori scuri, vero?
" bene, diciamo a vim di tenerne conto
set bg=dark

" usiamo gli spazi al posto del carattere di tabulazione
" da pythonista questo è fondamentale
set expandtab

" disabilitiamo il blinking del cursore in modalità normale
set gcr=n:blinkon0

" salviamo le ultime 100 righe di storia dei comandi
set history=100

" evidenziamo i termini trovati dalla ricerca
set hlsearch

" forziamo la ricerca incrementale, cioè salta al primo termine
" trovato anche durante la digitazione
set incsearch

" disabilitando la modalità retro-compatibilità, si attivano
" tutte le features di Vim (in opposizione a Vi)
set nocompatible

" disabilitiamo il wrap delle linee, le linee troppo lunghe
" non verranno mandate a capo creando confusione.
set nowrap

" mostriamo sempre i numeri di riga
set number

" mostriamo le coordinate, per riga e colonna, della posizione
" corrente del cursore
set ruler

" se è abilitata l’auto-indentazione, questa viene sostituita
" con 4 spazi
set shiftwidth=4

" mostra sempre l’output dei comandi nella barra di stato.
" Ad es. mostra il numero di righe selezionate
set showcmd

" evidenzia le parentesi corrispondenti
set showmatch

" sostituisce il carattere di tabulazione con 4 spazi
set tabstop=4

" disabilitiamo il wrap delle parole
set textwidth=0

" settiamo un numero di possibili undo abbastanza alto...tutti sbagliano
set undolevels=1000

" carattere da utilizzare per iniziare ad espandere le macro.
" Ad es. io ho impostato che scrivendo "pdb” e premendo TAB
" il testo viene sostituito con "import pdb;pdb.set_trace()”
set wildchar=<Tab>

" questa impostazione è una delle più comode, infatti quando digitiamo un
" comando incompleto e premiamo TAB, mostra un comodo menu al
" posto di ciclare su tutte le opzioni
set wildmenu

" impostiamo un set di colori predefinito
colorscheme desert

" abilitiamo sempre la colorazione del testo in funzione della sintassi riconosciuta
syntax on

" abilitiamo sempre la modalità paste, utile per evitare che
" al copia-incolla vengano inseriti tab non richiesti
set paste

" disabilitiamo l’autoindentazione, fa più danno che altro
set noautoindent

" perché non cambiare colore in modalità inserimento?
if &term =~ "xterm"
let &t_SI = "\<Esc>]12;orange\x7"
let &t_EI = "\<Esc>]12;white\x7"
endif

" questo comando permette di nascondere velocemente la colonna della numerazione
" per facilitare il copia/incolla del testo
nnoremap K :set nonumber!<CR>:set foldcolumn=0<CR>

" mostriamo un po' di utili informazioni nella status bar, es. nome e path del
" file aperto, se ci sono modifiche non salvate, riga e colonna del cursore,
" percentuale di avanzamento nella lettura del testo.
set statusline=%F%m%r%h%w\ %y\ [row=%l/%L]\ [col=%02v]\ [%02p%%]\

" ecco un comando veramente furbo. Capita sempre di aprire un file, cominciare
" a modificarlo, per poi scoprire che il file è aperto in sola lettura per
" questione di permessi di accesso. Bene: con questo comando, si forza vim
" a chiudere e riaprire il file con i permessi di sudo (richiedendo la password)
" e salvando il buffer.
cmap w!! %!sudo tee > /dev/null %

" shortcut molto comoda per trascinare una riga in alto o in basso,
" eventualmente scambiando di posizione con la riga di destinazione,
" semplicemente tenendo premuto CTRL e spostando la riga con le frecce
" in alto e in basso.
nmap <C-Up> ddkP
nmap <C-Down> ddp

" questo gruppo di shortcut semplifica lo spostamento del focus
" da una finestra all’altra, basta tenere premuto ALT e spostarsi con
" le frecce di direzione.
nmap <silent> <A-Up> :wincmd k<CR>
nmap <silent> <A-Down> :wincmd j<CR>
nmap <silent> <A-Left> :wincmd h<CR>
nmap <silent> <A-Right> :wincmd l<CR>

" premendo la combinazione di tasti “\ + l” si visualizzano/nascondono
" i caratteri nascosti, come ad esempio gli spazi a fine riga,
" e i caratteri di tabulazione
nmap <leader>l :set list!<CR>
