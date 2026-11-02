# B preparado en el checkout original

Se concentra la implementación en `experiment/fileAgent`, sin commit ni push.
Se recupera E2 y la integración duradera: registro antes de llamadas, presupuesto
protegido, contexto determinista, recibos y recuperación. Solo se admite B con
contexto preparado (`prepared`) o desactivado (`off`). Se retira la variante
sin vistas, el preparador de nueve ejecuciones y el worktree adicional.

Se conservan cambios independientes de investigación autónoma y sus documentos.
Las trazas históricas quedan como evidencia local bajo
`artifacts/e2-b-evidencia-retirada`, sin lanzadores ni nuevas ejecuciones.
Un respaldo local previo a la integración conserva los archivos reemplazados.
No se cambia FinMate, el wheel ni las credenciales.

La campaña preliminar mostró encargos pendientes aun con seis llamadas completas;
esta reorganización no corrige ni certifica su suficiencia semántica. No autoriza
otra campaña. El siguiente paso debe ser validar el recorrido de un encargo acotado.

## Verificación y retirada

127 pruebas locales de B, E2, controlador, casos fijos y V8 pasaron sin proveedores.
Mypy: 45 archivos sin errores. `git diff --check` sin errores.
Git desregistró el worktree y se eliminó su rama auxiliar. La eliminación física
quedó incompleta por rutas largas; la revisión automática rechazó el borrado
recursivo de los restos. Los lanzadores residuales se deshabilitaron. Ninguna
nueva campaña ni llamada real fue ejecutada en esta reorganización.
