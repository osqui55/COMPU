// Función para mover el fondo con el movimiento del ratón
window.onload = function() {
      document.onmousemove = function(e) {
        var x = -(e.clientX/5);
        var y = -(e.clientY/5);
        this.body.style.backgroundPosition = x + 'px ' + y + 'px';
		};
    };

// Funciones para check único y cambio automático del mismo
function check1(){
	if(document.fUmbral.Modo2.checked == true){
		document.fUmbral.Modo2.checked = false;
	}
}
function check2(){
	if(document.fUmbral.Modo1.checked == true){
		document.fUmbral.Modo1.checked = false;
	}
}

// Función de validacion de umbral y opciones del mismo
function validar(){
	if(document.fUmbral.Modo1.checked == false && document.fUmbral.Modo2.checked == false){
		alert("Debe seleccionar una opcion Historico/Actual")
		return false;
	}
	else{
		if(document.fUmbral.umbral.value.length == 0){
			alert("Debe introducir un umbral")
			return false;
		}
		else if(document.fUmbral.umbral.value >= 100){
			alert("Ha introducido el valor maximo o un numero mayor. Nunca se superara");
			return false;
		}
		else if(document.fUmbral.umbral.value < 0){
			alert("El umbral debe ser un numero positivo menor de 100");
			return false;
		}
		else{
			document.fUmbral.submit();
		}
	}
}	