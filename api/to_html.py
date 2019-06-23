# -*- coding:utf-8 -*-

BODY = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"> 
<title>{article_title}</title>
<link rel="stylesheet" href="https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css">  
</head>
<body style="
    margin-left:15%;
    margin-right:15%;
    text-indent:0; 
    word-spacing:1px;
    font-family: Helvetica，Arial;
    font-weight: 300;
    font-style: normal;
    font-size: 18px;
    line-height: 1.58;
    letter-spacing: -.003em;">
    
<h3 style="text-align: center;margin-bottom: 20px">{article_title}</h3>
<div style="margin-top: 20px;margin-bottom: 10px">
    <img src="https://vermouth2018.oss-cn-qingdao.aliyuncs.com/product/WX20190623-181707%402x.png?x-oss-process=style/xxx"
                                    alt="pycon2017" width="100%" height="100%">
</div>
{all_part}
</body>
</html>
"""

PART = """

<p class="text-muted">

{part_content}

</p>

"""
