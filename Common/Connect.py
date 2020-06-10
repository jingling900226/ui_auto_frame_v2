import paramiko
import logging
import time


class SSHClient:
    def __init__(self, ip, port, username, password):
        """
        初始化IP, 端口，用户名，密码，命令
        :param ip:  远程服务器ip
        :param port:  端口
        :param username:  用户名
        :param password:  密码

        """
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.ssh = None
        self.__connect_server()

    def __connect_server(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(self.ip, self.port, self.username, self.password, timeout=10)
        except Exception as e:
            logging.error('连接失败！%s' % e)

    def upload_file(self, local_file, remote_file):
        """
        文件上传
        :param local_file: 要上传的本地文件路径
        :param remote_file: 远端文件路径
        :return:
        """
        sftp = self.ssh.open_sftp()
        try:
            sftp.put(local_file, remote_file)
            logging.info('文件上传完成，{}'.format(local_file))
        except Exception as e:
            logging.error('文件上传失败！{}{}'.format(local_file, e))
        sftp.close()

    def close(self):
        """
        断开连接
        :return:
        """
        logging.info("Close SSH connection...")
        self.ssh.close()

    def execute_command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        stdout = stdout.read().decode("utf-8")
        stderr = stderr.read().decode("utf-8")
        return stdout, stderr


if __name__ == '__main__':
    ssh_client = SSHClient('10.5.16.224', 22, 'tester', '64391099@inhand')
    remote_path = '/home/tester/wangrc/dockerPro/nginx/report'
    ssh_client.upload_file('/home/inhand/下载/artifacts.zip', remote_path + '/artifacts.zip')
    time.sleep(2)
    command1 = 'unzip {}/artifacts.zip -d {}'.format(remote_path, remote_path)
    command2 = 'mv {}/Report/allure-report/* {}/'.format(remote_path, remote_path)
    ssh_client.execute_command(command1)
    ssh_client.execute_command(command2)
    ssh_client.close()
