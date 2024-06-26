# -*- coding: utf-8 -*-
# @Author : buyfakett
# @Time : 2023/12/29 14:21
import logging

import jwt
from jwt import exceptions
import datetime
from fastapi import Header, HTTPException
from starlette import status
from pyconfig_util.config_util import setting


# 创建 JWT token
def create_token(user_id: int, is_admin: bool = True, day: int = 99999):
    """
    :param user_id: 用户id
    :param day:  日期。单位天 ，默认99999天
    :return:     生成的token
    """
    # 构造header
    headers = {
        'typ': 'jwt',
        'alg': 'HS256'
    }
    # 构造payload，根据需要自定义用户内容
    payload = {
        'user_id': user_id,  # 自定义用户ID
        'is_admin': is_admin,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(day)
    }
    # 密钥
    SALT = str(setting.CONFIG_TOKEN_PRIVATE_KEY)
    token = jwt.encode(payload=payload, key=SALT, algorithm="HS256", headers=headers).decode('utf-8')
    return token


# 验证 JWT token
def verify_token(Authorization: str = Header(None)):
    token = Authorization
    # 密钥，必须跟签发token的一样
    salt = str(setting.CONFIG_TOKEN_PRIVATE_KEY)
    # 从请求头中获取token
    # 判断url在不在白名单中
    if not token:
        message = '没有携带token'
        logging.error(f'token验证结果：{message}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
        )
    try:
        # jwt提供了通过三段token，取出payload的方法，并且有校验功能
        # 这个是我们签发时，封装的payload字典
        decoded_token = jwt.decode(jwt=token, key=salt, verify=True)
        # 从解码后的 token 中获取 user_id和is_admin 字段
        user_id = decoded_token.get('user_id')
        is_admin = decoded_token.get('is_admin')
    except exceptions.ExpiredSignatureError:
        message = 'token已失效'
        logging.error(f'token验证结果：{message}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
        )
    except jwt.DecodeError:
        message = 'token认证失败'
        logging.error(f'token验证结果：{message}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
        )
    except jwt.InvalidTokenError:
        message = '非法的token'
        logging.error(f'token验证结果：{message}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
        )
    except Exception as e:
        logging.error(f'token验证结果：{str(e)}')
        # 所有异常都会走到这
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{str(e)}",
        )
    user_info = {
        'user_id': user_id,
        'is_admin': is_admin,
    }
    return user_info
