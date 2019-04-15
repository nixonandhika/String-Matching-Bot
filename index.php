<html>
<head>
    <title>Slothy Chatbot</title>
    <script type = "text/javascript">
        var vid = document.getElementById('avatar');
        function playvideo(){
          if(vid.onpause()){
            vid.play();
          }
        }
    </script>
</head>
<body>
  <center>
  <video autoplay name="avatar" poster="poster.png" width="500" height="500">
      <source src="avatar.webm" type="video/webm">
      <img src="video.gif" width="400" height="300">
    Your browser does not support webm video
  </video>
  <form action="#" method="post" onsubmit="playvideo();return false">
    Enter text: <input name="query" type="text">
    <input type="submit">
  </form>
  <?php
    if(isset($_POST['query'])){
        $query = $_POST["query"];
        echo $query;
    }
  ?>
  </center>
</body>
</html>
