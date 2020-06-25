#代码目录说明
公共的方法目录：common
测试用例类模块目录：testcases
测试数据目录：data
测试报告存放目录：reports
存放一些下载第三方的模块：library
配置文件存放目录：conf
日志文件存放的目录：logs
项目文件所有文件夹路径:filePath
项目的启动文件：run_test
中间层: middlerware

#脚本使用说明
    步骤:
    一,修改相关配置
        report:
          title: 设置报告标题
          description: 设置该报告描述
          tester: 测试人员
         
        excel:
          excelname: 设置测试数据的excel文件
          registersheet: 注册数据
          loginsheet: 登陆数据
          rechargesheet: 充值数据
          withdrawsheet: 提现数据
          addsheet: 新增项目数据
          auditsheet: 审核数据

        sql:
          host: 数据库域名
          port: 数据库端口号
          user: 登陆账号
          password: 密码
          charset: 编解码方式(utf8 不能为utf-8)
         
        user:
           mobile_phone: 测试账号
           pwd: 测试账号密码

        admin_user:
            mobile_phone:管理员账号
            pwd:管理员测试账号密码

         host: 测试域名
    
    二,运行run_test.py