# NCF DGII Reports

Este módulo para ODOO 11 implementa los reportes de los números de comprobantes fiscales (NCF) para el cumplimento de la norma 06-18 de la Dirección de Impuestos Internos (DGII) en la República Dominicana, así como una guía para los reportes del ITBIS (IT1) y del anexo A del IT-1 (ITA). Ha sido probado en una empresa de servicios básica y necesita validaciones y calculos extras para ser implementado en negocios de personas físicas que usan su cédula como RNC, empresas de construcción, empresas de telecomunicaciones y proveedores del estado.

Este repositorio tiene como objetivo que este módulo sea integrado en https://github.com/odoo-dominicana/l10n-dominicana y que sea mantenido por la comunidad de ODOO Dominicana.  Mientras tanto todo aquel que desee colaborar, puede hacer un Pull Request aquí.

## CONFIGURAR IMPUESTOS
Se debe configurar correctamente los impuestos, para ello ir al listado de impuestos y en la opción de Tipo de Impuesto de Compra (Cuando el Ámbito del Impuesto es Compra) seleccionar la opción adecuada para cada caso.

## CONFIGURAR CORRECTAMENTE LOS TIPOS DE PRODUCTOS
En cada producto, se debe configurar correctamente el "Tipo de Producto" para poder filtrar el "Monto Facturado en Servicios" y el "Monto Facturado en Bienes".  Actualmente si un producto es del tipo "Servicio" pues se suma al Monto Facturado en Servicios y si es otra cosa como puede ser Consumible o Almacenable, entonces lo sumamos al Monto Facturado en Bienes.  OJO que si venden productos digitales (como libros, fotos, etc..) en teoría serían servicios al no ser algo mateiral pero esto tampoco lo estamos filtrado en la actualidad y en dado caso de ponerlo caerían como Bienes.

## CONFIGURAR LA(S) CUENTA(S) QUE ES(SON) USADA(S) PARA EL ITBIS RETENIDO EN VENTAS (REPORTE 607) SEGÚN LA NORMA 02-05
En el catálogo de cuentas hemos colocado un nuevo campo opcional para escoger, este se llama: **Tipo de Impuesto en Venta** y por lo general las empresas que tiene RNC solo deberán escoger allí la primera opción **ITBIS Retenido Persona Jurídica (N 02-05)** y cuando la cuenta sea *ITBIS Retenido Persona Jurídica (N 02-05)* que por defecto en el catálogo de cuentas dominicano en ODOO 11 es la *no.21030201* y tiene el ID 100.

Con esta acción podemos obtener las columnas *7 - FECHA DE RETENCIÓN* y *10 - ITBIS RETENIDO POR TERCEROS* del reporte 607.


## REGISTRAR CORRECTAMENTE LAS FACTURAS DE PROVEEDORES QUE NOS DAN UN SERVICIO Y AL CUAL LE HACEMOS RETENCIÓN DE 30% ITBIS (REPORTE 606) SEGÚN LA NORMA 02-05
Al registrar los impuestos de este tipo de factura, se debe seleccionar el **18% de ITBIS compra (servicios)** y además como le vamos a hacer retención de 30% ITBIS según la norma 02-05, debemos seleccionar también como impuesto **Retención ITBIS 30% a Persona Jurídica (Servicios)** y que por defecto ese impuesto viene atado a la cuenta contable **21030201 - ITBIS Retenido Persona Jurídica (N 02-05)**, además recordar que ese impuesto se debe configurar como **ITBIS retenido**

Con esta acción podemos obtener la columna *12 - ITBIS RETENIDO* del reporte 606.

*Nota: del mismo modo, otro impuesto a escoger podría ser el Retención ISR 10% a Personas Físicas en los casos que aplique* 


### ESTADO ACTUAL  

- 606 en Alpha 3 (ver ISSUES AND PENDING STUFF) .
- 607 en Alpha 2 (ver ISSUES AND PENDING STUFF) .
- 608 y 609 en pendiente de desarrollo.
- Guía del ITA (Anexo A del IT1) en Alpha 1
- Guía del IT1 (Declaración de ITBIS) en Alpha 1

## RECOMENDACIONES
Luego de implementar este módulo, se recomienda hacer una revisión manual de los reportes al menos durante 3 períodos en búsca de bugs y cada vez que en un determinado período tenga novedades nuevas antes no usadas como puede ser recibir una Nota de Crédito y otros.

## LICENCIA DE USO, DESCARGO DE RESPONSABILIDAD, AYUDA Y SOPORTE
 Este módulo “software” (programa) es de código fuente libre y abierto y está licenciado bajo la GNU General Public License Version 3 (https://www.gnu.org/copyleft/gpl.html). 

 Al usar el módulo, usted se compromete a darle un uso de conformidad con la leyes dominicanas. 
 
 Este módulo se suministra tal cual es. Por diversas razones no podemos garantizar de forma expresa o implícita, la confiabilidad o integridad de los reportes que emite este módulo, y que los mismos estén libre de fallos debido a códigos o rutinas de programación incorrectos.

 Para ayuda puede escribir un issue en este repositorio o vía la comunidad de ODOO Dominicana.  Si necesita soporte e implementaciones puede contactar con Manuel Gonzalez en SOFTNET TEAM SRL (https://www.softnet.do)



## ENDING STUFF

- Ver todos los #TODO en el código.
- Terminar Anexos Del IT-1



### Créditos:  Basado en el trabajo de Eneldo Serrata para Marcos Organizador de Negocios SRL. (https://marcos.do/) 


### Autor: Manuel Gonzalez para SOFTNET TEAM SRL (https://www.softnet.do)

### Colaborardor: Jeffry De La Rosa para SOFTNET TEAM SRL (https://www.softnet.do)
