var jobmy;
if (!jobmy) { jobmy = {}; }

jobmy.putJob = function() {
  let title = $("#title").val();
  let remarks = $("#remarks").val();
  let command = $("#command").val();
  let schedule = $("#schedule").val();
  let data = {
    "title": title,
    "remarks": remarks,
    "command": command,
    "schedule": schedule
  };
  console.log(data);
  $.ajax({
    type: "POST",
    url: "/job_edit",
    data: data,
    xhrFields: {
      withCredentials: true
    },
    success: function(result, textStatus) {
        let ret = eval(result);
        $("#msg").html(ret["msg"]);
    },
    error: function(xhr, textStatus, errorThrown) {
      console.log(xhr);
    },
    complete: function() {
      console.log("finish jobmy.putJob");
    }
  });
}

jobmy.executeJob = function(jobId) {
  let data = {
    "job_id": jobId
  };
  console.log(data);
  $.ajax({
    type: "POST",
    url: "/job_execute",
    data: data,
    xhrFields: {
      withCredentials: true
    },
    success: function(result, textStatus) {
        let ret = eval(result);
        window.alert(ret["msg"]);
    },
    error: function(xhr, textStatus, errorThrown) {
      console.log(xhr);
      window.alert("error happend.");
    },
    complete: function() {
      console.log("finish jobmy.putJob");
    }
  });
}
