Cliente:
llega a la red y hace broadcast
Tiene una lista de nodos que le respondieron a este broadcast
Toma al primero y establece conexion con el, si no puede, entonces lo 
desechas y toma al segundo de la lista.
El broadcast solo sera contestado por servidores, que son los que sabran del mensaje de respuesta indicado.
A ese servidor le puedes pedir su lista de musica, la lista de musica de todos los nodos, y le puedes pedir que te muestre las de todos.
puede pedir una cancion determinada, y si en algun servidor esta te va a decir a quien puedes pedirsela.

El debe pasarte la musica o solo reproducirla? 
Se puede reproducir una musica sin pasarla realmente, sin pasarla fisicamente?
Existe la forma de pasar temporalmente musica tcp sin ocupar espacio de la memoria?

Servidor:
Tiene que contestar al broadcast. Atendera peticiones por un puerto determinado(hasta 100 por ejemplo) de clientes que solo le pediran listas de musica y musica en especifico.
Atenderá por otro puerto las peticiones de los otros servidores que seran sobre si tiene una cancion en especifico, su lista de musica, sobre quien es su padre o su antecesor, algunas serán para replicar musica también.
La comunicacion con los otros server se hara usando chord, esto garantiza replicación y localizacion, ademas de seguridad en el sistema.


Tareas para Hoy:
-Hacer el cliente, que esta facilito(menos el broadcast)
-lograr que que cliente se conecte con un servidor y se pasen archivos usando tcp

Tareas Martes:
-Lograr cuando se le pide al servidor la cancion este le devuelve los k que la tienen(que en este caso seran fijos) y el cliente escoge tres y se pasa la cancion por pedacitos, si uno se cae, coge desde el principio el pedazo que falta de otro de la lista,y asi hasta que revise toda la lista hasta que llegue al ultimo, si le queda algun pedazo por pasar, va desde el principio de la lista pidiendo que le pasen ese pedacito;si nadie puede pasarlo, ella vuelve a hacer la peticion general y si nadie la tiene entonces damos el mesaje de, no esta la canción.

Tarea Miercoles y jueves y viernes y sabado y domingo:
Hacer chord

Tarea Lunes:
-El servidor busca por chord quien tiene las canciones y se las pasa al cliente en vez de darle servidores en especificos
-porbar la red, la tolerancia a fallas(seguro encontramos fallos)
.
.
.
.
.
.
Tratar de Hacer interfaz gráfica si es posible.
