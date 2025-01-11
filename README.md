# Python game Project

## Authors: Buzatu Calin-Cristian, Calofir Mihnea, Sirbu-Cretu Antonio Mihai.

Aplicatia: Platformer 2D - Shifting Realms
Link Github: https://github.com/klinbzt/pythongame

I. MODUL DE FUNCTIONARE, PE SCURT ( aprofundat in punctul II )

La rularea jocului, apare meniul de start, cu diferite optiuni. Printre acestea, se numare: Pornirea jocului de la inceput ( planeta 0, level 0 ), pornirea de la o salvare anterioara ( prin load game ), un meniu de setari, din care se pot configura luminozitatea, volumul sau aspect ratio-ul ecranului.

Jocul este impartit in planete, fiecare planeta fiind impartite in mai multe levele. Fiecare planeta are ca punct diferential forta gravitationala. Datele despre acestea sunt preluate dintr-un json, iar aceste date sunt procesate in LevelManager, care: da load planetei curente, da load level-ului curent al planetei, ruleaza level-ul tocmai instantiat. Atunci cand un nivel este finalizat, functia de callback este invocata, ceea ce declanseaza load-area urmatorului level al planetei / urmatoarei planete, daca cea curenta a fost parcursa in intregime.

Singura entitate din joc, in acest moment, este player-ul. Acesta are mai multe abilitati, pe care le poate sau nu efectua in functie de permisiunile level-ului ( preluate din json ). Sunt implementate: Left / Right movement, Jump, Wall Jump, Wall Slide, Dash, Heavy_Mode ( dubleaza masa player-ului ), Light_Mode ( injumatateste masa player-ului ). Pentru ca masa unei entitati intra in calculul fortei cu care este tras spre sol, aceste moduri vin in completarea gravitatiei aplicata de fiecare planeta, in functie de forta gravitationala a instantei Planet curente.

Scopul jocului este atingerea flag-ului de catre player, in fiecare level. Jocul ar trebui sa fie un platformer de tip puzzle ( chiar daca nu am reusit inca sa implementam nivele suficient de inteligente :D ). Pe viitor, am dori sa adaugam si o poveste, prin casetele de text animat implementate deja.

II. IMPLEMENTAREA

Jocul este impartit in mai multe planete, fiecare cu propriile ei date. Acestea sunt:
-> name ( numele planetei )
-> gravity_strength ( forta gravitationala a planetei. TEORETIC, in jurul acesteia ar trebui centrat level design-ul fiecarui nivel)
-> levels ( un array de dictionare, fiecare incapsuland datele nivelelor de pe planeta respectiva )

Un level are urmatoarele date:
-> tmx_map ( path-ul catre fisierul .tmx generat de Tiled - level-ul in sine )
-> permissions ( permisiunile abilitatilor pe care player-ul le are la dispozitie intr-un anumit level; True daca player-ul poate folosi abilitatea respectiva, False in caz contrar )

In assets, avem directoare pentru diversele imagini, sunete sau font-uri folosite in realizarea jocului:
-> Graphics: png-uri pentru asseturile folosite in levele, png-uri pentru abilitati precum Dash, png-uri pentru meniu.
-> Sounds: effectele sonore pentru actiuni precum Jump, muzica de fundal, etc
-> Tilesets: fisiere .xml pentru configurarea felului in care se randeaza un anumit asset ( png )
-> Fonts: neutilizat in versiunea actuala a jocului

In Levels:
-> Directoare pentru fiecare planeta din joc, fiecare director continand fisierul json de configurare a planetei si nivelele acesteia, in format .tmx

In src:
Am incercat sa modularizam felul in care lucram, folosind clase pentru a reutiliza cat mai mult cod, cat mai eficient.

-> main.py: Acest fisier contine loop-ul principal al jocului. Clasa Game creeaza instante precum LevelManager si StartupScreen, iar in metoda run(), jocul este pornit.

-> utils: Director in care se afla fisierele cu clase utilizate in mai multe zone ale codului si cu utilizari variabile, constante, etc.
--> settings.py: Constante, import-uri generale, etc
--> timer.py: Clasa Timer, care activeaza, updateaza si dezactiveaza timere. Folosita pentru a tine cont cat timp a trecut de la o actiune, daca o actiune se afla in desfasurare, etc

-> ui: Director in care se afla fisierele ce tin de aspectele vizuale, separate de jocul propriu-zis. Printre acestea, se numara:
--> startup.py: Contine clasa StartupScreen, care se ocupa de randarea unui meniu de start si redirectionarea player-ului catre diferite optiuni, atunci cand acesta doreste sa le acceseze.
--> menusettings.py: Contine clasa SettingsMenu, care se ocupa de randarea unui meniu de setari, care include: brightness, volume, fullscreen.
--> savegame.py: Contine clasa SaveGame care se ocupa de randarea unui meniu de salvare a nivelului curent.
--> loadgame.py: Contine clasa LoadGame care ofera posibilitatea de a da load unui nivel salvat anterior din meniul de start.
--> textbox.py, animatedtext.py: Contin clase prin intermediul caruia fiecare nivel poate randa casete de text animate, in scopul informarii player-ului despre planeta curenta, abilitati deblocate, etc

-> planets
--> planet.py: Contine clasa Planet, care se ocupa de aplicarea gravitatiei asupra entitatilor din joc ( momentan, singura entitate din joc este player-ul, restul sunt considerate obiecte / platforme / tile-uri / decor ). In plus, este implementata, dar nu si folosita ( inca ), metoda reverse_gravity, care inverseaza gravitatia planetei. Ar putea conduce la creeare unor nivele interesanta, ne gandeam la un timer cu un timp random la care planeta isi inverseaza gravitatia. To be implemented... De asemenea, clasa instantiaza un AudioManager, in eventualitatea in care pe viitor, implementam efecte sonore diferite pentru fiecare planeta in parte

-> levels
--> level_manager.py: Contine clasa LevelManager, care sta la baza jocului. Aici se da load planetei curente ( extragere de date din json ) si nivelului curent al planetei ( incarcarea hartii, instantierea unui Level ). Fiecarei instante Level ii este pasat un callback. Cand player-ul termina un nivel, se apeleaza callback-ul, care incarca urmatorul nivel al planetei curente. In cazul in care toate nivele unei planete au fost finalizate, se incarca urmatoarea planeta. In plus, de aici se incarca salvarile facute de player in timpul jocului, prin functiile get_save_info() si load_save_info(), care fac legatura intre sistemul de management al jocului si meniul de start.
--> level.py: Contine clasa Level , care creeaza sprite-urile din diferite layere folosite in nivel. Exemple ar fi: Terrain, Damage_Tiles, Objects, Moving Objects, Decorations. Dupa setup, nivelul porneste. Prin functia check_constraints() este implementata o camera pe axa Ox, iar player-ul nu poate iesi din zona hartii pe aceasta axa. In plus, tot in clasa Level, functia draw_permissions() randeaza abilitatile disponibile player-ului si disponibilitatea acestora ( folosita, in curs de folosire, etc ).
--> flag.py: Contine clasa Flag, care verifica daca player-ul a atins sfarsitul nivelului.

-> sprites: Director ce contine clase care gestioneaza modul in care sunt randate asseturile pe ecran, daca sunt collidable, etc

-> entities
--> player.py: Momentan, singura entitate din joc este player-ul ( nu am implementat inamici ). Clasa Player se ocupa de tot ce tine de player: coliziuni cu terenul si platforme, movements, abilitati, animatii, efecte sonore la anumite miscari, respawn ( in cazul in care player-ul moare sau cade de pe harta ). Player-ul dispune de urmatoarele abilitati:
---> Left movement, Right movement
---> Jump, Wall Jump ( pentru scurt timp atunci cand atinge un perete ), Wall Slide
---> Dash ( cooldown de o secunda )
---> Heavy_Mode ( masa player-ului se dubleaza ), Light_Mode ( masa player-ului se injumatateste ). Intrucat masa unei entitati, la fel ca in viata, influenteaza forta cu care este tras spre pamant, ideea din spatele acestor abilitati este de a diminua / amplifica gravitatia planetei in unele puncte ale nivelelor ( nu am reusit sa implementam niste nivele suficient de elocvente pentru a le arata felul in care ar trebui folosite, to be implemented... )

-> audio
--> audio_manager.py: Contine clasa AudioManager din care se pornesc / opresc efecte sonore sau muzica de fundal, se seteaza un volum ( individual sau comun ). Momentan, fiecare instanta de AudioManager da load acelorasi efecte sonore. Totusi, prin pasarea unui dictionar de efecte sonore ca parametru, preluat din json-ul unei planete, fiecare planeta poate beneficia de efecte sonore diferite.

III. TEHNOLOGII

Pygame -> pentru tot ce tine de partea de cod sau randarea unor imagini, rularea unor efecte sonore, etc
Tiled -> pentru level design ( fisierele .tmx )

Am vrut sa ne facem propriile caractere intr-un software de creare pixel art, precum Piskel. Am descoperit ca o saptamana nu este suficient timp pentru a invata pixel art. Data viitoare :D ( momentan, folosim asseturi gratuite preluate de pe net )

IV. CONTRIBUTII

Buzatu Calin-Cristian:
-> Tot ce se afla in directorul src/ui/, adica:
--> Startup Screen + toate meniurile aferente
--> Sistemul de load si save game
--> Casetele de text animate
-> A facut merge la branch-uri ( are respectul tuturor membrilor echipei )

Dificultati intampinate:

Calofir Mihnea:
-> Directorul levels/ si sistemul de parsare de date per planeta / per level
-> Clasa Player: coliziuni cu terenul si platforme, movements, abilitati, animatii, efecte sonore la anumite miscari, respawn, etc
-> Clasa AudioManager
-> Clasa Timer
-> Clasa Planet: aplicarea gravitatiei asupra entitatilor, inversarea gravitatiei ( to be used in later versions )
-> Clasa LevelManager ( fara partea de salvare a unui nivel sau de loadare a unui nivel salvat )
-> Clasa Level ( fara prelucrarea a catorva layere, randarea box-urilor de abilitati disponibile )
-> O parte din prelucrarea si interactiunea sprite-urilor
-> Level Design:
--> Planeta 0 - 4 levele
--> Planetele 1, 2, 3 - aceleasi 2 nivele facute initial in procesul de creare al abilitatilor
--> Planeta 1 - un nivel cu asseturi diferite ( ideea era ca fiecare planeta sa aiba un anumit biom, iar planeta 1 ar corespune Pamantului - biom de... pamant? Idk, am vrut sa semene cu introducere in Hollow Knight, a iesit introducerea in minecraft, dar crapy )

Dificultati intampinate: Cea mai importanta, un bug care facea player-ul sa cada de pe harta inainte de randarea nivelului. Am stat pana la 4 dimineata sa identific bug-ul. Am scris 15 caractere ( 2 linii de cod ) ca sa il rezolv. Alte dificultati: Animatia de dash a player-ului, coliziuni cu wall-ul ( partea de wall slide si wall jump ), TILED! TILED! TILED! Nu mai fac level design in viata mea

Sirbu-Cretu Antonio Mihai:
-> Implementarea initiala a partii de audio
-> Implementarea restrictiilor per nivel ( player-ul nu poate iesi din harta pe axa OX)
-> Implementarea texturilor ( + cautarea de asseturi )
-> Implementarea initiala a versiunii de Death a player-ului ( inlocuita cu respawn-ul, insa folosita o buna parte din procesul de creare a jocului )
-> Implementarea unei camere bidirectionale, care urmarea player-ul atat pe axa OX cat si pe axa OY ( inlocuita tot de el in favoarea unui sistem care se concentreaza pe axa OX )
-> Randarea abilitatilor disponibile per level
-> Identificarea si debuggarea unor portiuni de cod cu probleme

Dificultati intampinate:
