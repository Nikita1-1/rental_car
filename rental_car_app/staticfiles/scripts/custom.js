const btn = document.querySelector(".fancy-burger");
        const menu = document.querySelector("#classMenu");
        

        btn.addEventListener("click", () => {
        btn.querySelectorAll("span").forEach((span) => span.classList.toggle("open"));
        menu.classList.toggle("open");
        });

function makeAjaxCall(){
        $.ajax({
                url: "/update_booking_status/",
                type: "GET",
                success: function(data){
                        console.log("checked Car")

                },
        });
}

setInterval(makeAjaxCall, 600000); 

