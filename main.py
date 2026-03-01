import sys
import os
import random
import time
import math
import numpy as np
from typing import cast
import OpenGL.GL as gl
import OpenGL.GLU as glu
import glfw
from PIL import Image

# 添加mmdpy模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'mmdpy'))

import mmdpy
import mmdpy_world

class CustomWorld(mmdpy_world.world):
    """自定义世界类，支持背景图片"""
    
    def __init__(self, window_name: str, window_width: int, window_height: int):
        # 调用父类初始化
        super().__init__(window_name, window_width, window_height)
        
        # 设置窗口图标
        self.set_window_icon()
        
        # 加载随机背景图片
        self.background_texture = self.load_random_background()
        
        # 添加时间追踪，用于平滑动画
        self.start_time = time.time()
        self.last_time = self.start_time
    
    def set_window_icon(self):
        """设置窗口图标为144.ico"""
        try:
            icon_path = "144.ico"
            if os.path.exists(icon_path):
                # 使用PIL加载图标
                icon_image = Image.open(icon_path)
                
                # 转换为RGBA格式
                if icon_image.mode != 'RGBA':
                    icon_image = icon_image.convert('RGBA')
                
                # 获取图像数据
                icon_width, icon_height = icon_image.size
                
                # 将图像转换为numpy数组
                icon_array = np.array(icon_image)
                
                # 设置窗口图标 - 使用正确的参数格式
                glfw.set_window_icon(self.window, 1, [(icon_width, icon_height, icon_array)])
                print(f"窗口图标设置成功: {icon_path}")
            else:
                print(f"图标文件不存在: {icon_path}")
        except Exception as e:
            print(f"设置窗口图标失败: {e}")
            import traceback
            traceback.print_exc()
        
    def load_random_background(self):
        """从png文件夹随机加载一张背景图片"""
        png_folder = "png"
        
        # 检查文件夹是否存在
        if not os.path.exists(png_folder):
            print(f"背景图片文件夹不存在: {png_folder}")
            return None
            
        # 获取所有png文件
        png_files = [f for f in os.listdir(png_folder) if f.lower().endswith('.png')]
        
        if not png_files:
            print("png文件夹中没有找到PNG图片")
            return None
            
        # 随机选择一张图片
        selected_image = random.choice(png_files)
        image_path = os.path.join(png_folder, selected_image)
        
        print(f"使用背景图片: {selected_image}")
        
        try:
            # 加载图片
            image = Image.open(image_path)
            
            # 转换为RGB格式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 获取图片尺寸
            width, height = image.size
            print(f"图片尺寸: {width}x{height}")
            
            # 调整图片大小，避免尺寸过大
            max_size = 2048
            if width > max_size or height > max_size:
                ratio = min(max_size / width, max_size / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                image = image.resize((new_width, new_height), Image.LANCZOS)
                print(f"调整图片尺寸为: {new_width}x{new_height}")
                width, height = new_width, new_height
            
            # 生成纹理
            texture = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
            
            # 设置纹理参数
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
            
            # 上传纹理数据
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, image.tobytes())
            
            # 检查OpenGL错误
            error = gl.glGetError()
            if error != gl.GL_NO_ERROR:
                print(f"OpenGL错误: {error}")
            
            # 解绑纹理
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
            
            print("背景纹理加载成功")
            return texture
            
        except Exception as e:
            print(f"加载背景图片失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def draw_background(self):
        """绘制背景图片"""
        if self.background_texture is None:
            return
            
        try:
            # 保存当前矩阵
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glPushMatrix()
            gl.glLoadIdentity()
            gl.glOrtho(0, self.window_width, 0, self.window_height, -1, 1)
            
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPushMatrix()
            gl.glLoadIdentity()
            
            # 禁用深度测试
            gl.glDisable(gl.GL_DEPTH_TEST)
            
            # 启用纹理
            gl.glEnable(gl.GL_TEXTURE_2D)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.background_texture)
            
            # 设置颜色为白色
            gl.glColor4f(1.0, 1.0, 1.0, 1.0)
            
            # 绘制四边形，覆盖整个窗口
            gl.glBegin(gl.GL_QUADS)
            gl.glTexCoord2f(0, 0); gl.glVertex2f(0, 0)
            gl.glTexCoord2f(1, 0); gl.glVertex2f(self.window_width, 0)
            gl.glTexCoord2f(1, 1); gl.glVertex2f(self.window_width, self.window_height)
            gl.glTexCoord2f(0, 1); gl.glVertex2f(0, self.window_height)
            gl.glEnd()
            
            # 禁用纹理
            gl.glDisable(gl.GL_TEXTURE_2D)
            
            # 恢复深度测试
            gl.glEnable(gl.GL_DEPTH_TEST)
            
            # 恢复矩阵
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glPopMatrix()
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPopMatrix()
        except Exception as e:
            print(f"绘制背景时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self) -> bool:
        """重写run方法，添加背景绘制"""
        if glfw.window_should_close(self.window):
            return True

        # 清除颜色和深度缓冲区
        gl.glClear(cast(int, gl.GL_COLOR_BUFFER_BIT) | cast(int, gl.GL_DEPTH_BUFFER_BIT))
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        # 绘制背景
        self.draw_background()

        # 设置透视投影
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluPerspective(45.0, float(self.window_width) / float(self.window_height), 0.10, 160.0)
        
        # 设置相机
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        glu.gluLookAt(0.0, 10.0, -30.0, 0.0, 10.0, 0.0, 0.0, 1.0, 0.0)

        # 渲染模型
        for model in self.models:
            model.draw()

        # 执行OpenGL命令
        gl.glFlush()

        # 交换前后缓冲区
        glfw.swap_buffers(self.window)

        # 轮询和处理事件
        glfw.poll_events()

        # 等待
        glfw.wait_events_timeout(max(0.00, 1. / 60 - self.fps_calc.elapsed_time()))

        return False

class HairPhysicsSimulator:
    """简单的麻花辫物理模拟器"""
    def __init__(self):
        self.gravity = np.array([0, 15.0, 0]) * 0.02  # 增加重力，使麻花辫更明显地向下
        self.damping = 0.9  # 减少阻尼，使动作更自然
        self.segments = []  # 存储每个麻花辫段的位置和速度
        
    def init_hair_segments(self, hair_bones):
        """初始化麻花辫段"""
        self.segments = []
        
        # 按左右分组，正确识别MaWei骨骼
        left_bones = [b for b in hair_bones if 'MaWei_L' in b.name]
        right_bones = [b for b in hair_bones if 'MaWei_R' in b.name]
        
        # 初始化左侧麻花辫
        for i, bone in enumerate(sorted(left_bones, key=lambda b: int(b.name.split('_')[2]) if '_' in b.name and len(b.name.split('_')) >= 3 else 0)):
            # 获取初始位置
            pos = bone.get_position()
            # 设置初始位置，从头部侧面开始，更自然的位置
            # 头部位置大约在Y=10左右，麻花辫应该从头部侧面开始下垂
            init_x = -3.0  # 左侧，更远离头部
            init_y = 15.0 + i * 0.8  # 从更高位置开始，每段增加0.8（更极端的向下）
            init_z = 2.0  # 更向前，远离眼睛
            init_pos = np.array([init_x, init_y, init_z])
            self.segments.append({
                'bone': bone,
                'position': init_pos,
                'velocity': np.zeros(3),
                'is_left': True,
                'original_pos': np.array(pos)  # 保存原始位置
            })
        
        # 初始化右侧麻花辫
        for i, bone in enumerate(sorted(right_bones, key=lambda b: int(b.name.split('_')[2]) if '_' in b.name and len(b.name.split('_')) >= 3 else 0)):
            # 获取初始位置
            pos = bone.get_position()
            # 设置初始位置，从头部侧面开始，更自然的位置
            init_x = 3.0  # 右侧，更远离头部
            init_y = 15.0 + i * 0.8  # 从更高位置开始，每段增加0.8（更极端的向下）
            init_z = 2.0  # 更向前，远离眼睛
            init_pos = np.array([init_x, init_y, init_z])
            self.segments.append({
                'bone': bone,
                'position': init_pos,
                'velocity': np.zeros(3),
                'is_left': False,
                'original_pos': np.array(pos)  # 保存原始位置
            })
    
    def update(self, dt=0.016):
        """更新物理模拟"""
        # 更新每个段
        for i, segment in enumerate(self.segments):
            # 应用重力
            segment['velocity'] += self.gravity * dt
            
            # 应用阻尼
            segment['velocity'] *= self.damping
            
            # 添加轻微的随机风力，使动作更自然
            wind_force = np.array([
                np.sin(time.time() * 2 + i) * 0.01,
                0,
                np.cos(time.time() * 1.5 + i) * 0.01
            ])
            segment['velocity'] += wind_force
            
            # 更新位置
            segment['position'] += segment['velocity'] * dt
            
            # 约束到前一段
            if i > 0:
                prev_segment = self.segments[i-1]
                # 计算到前一段的距离
                diff = segment['position'] - prev_segment['position']
                distance = np.linalg.norm(diff)
                
                # 目标距离（保持麻花辫长度）
                target_distance = 0.6  # 减小段间距，使麻花辫更紧凑
                
                # 如果距离大于目标距离，拉回
                if distance > target_distance:
                    direction = diff / distance
                    segment['position'] = prev_segment['position'] + direction * target_distance
                    
                    # 调整速度
                    segment['velocity'] *= 0.5
            else:
                # 第一段固定在头部附近
                if segment['is_left']:
                    # 左侧固定点 - 调整到更自然的头部侧面位置
                    segment['position'][0] = -3.0  # 更远离头部
                    segment['position'][1] = 15.0   # 更高位置
                    segment['position'][2] = 2.0    # 更向前
                else:
                    # 右侧固定点 - 调整到更自然的头部侧面位置
                    segment['position'][0] = 3.0   # 更远离头部
                    segment['position'][1] = 15.0   # 更高位置
                    segment['position'][2] = 2.0    # 更向前
            
            # 应用位置到骨骼
            bone = segment['bone']
            if hasattr(bone, 'set_position'):
                bone.set_position(segment['position'])
            elif hasattr(bone, 'setPosition'):
                bone.setPosition(segment['position'][0], segment['position'][1], segment['position'][2])

def fix_hair_bones_position(model):
    """直接控制麻花辫骨骼到正确位置，模拟物理下垂效果"""
    if not hasattr(model, 'bones'):
        print("模型没有骨骼信息，无法修复麻花辫位置")
        return
    
    try:
        # 查找麻花辫相关的骨骼
        left_hair_bones = []
        right_hair_bones = []
        
        for bone in model.bones:
            if 'MaWei_L' in bone.name:
                left_hair_bones.append(bone)
            elif 'MaWei_R' in bone.name:
                right_hair_bones.append(bone)
        
        print(f"找到 {len(left_hair_bones)} 个左侧麻花辫骨骼, {len(right_hair_bones)} 个右侧麻花辫骨骼")
        
        # 对左侧麻花辫骨骼，应用正确的位置
        for i, bone in enumerate(sorted(left_hair_bones, key=lambda b: int(b.name.split('_')[2]) if '_' in b.name and len(b.name.split('_')) >= 3 else 0)):
            # 获取当前位置
            current_pos = bone.get_position()
            
            # 设置正确的位置，从头部侧面开始自然下垂
            # 左侧麻花辫应该在头部左侧(X负值)，从头部高度(Y=15)开始下垂
            target_x = -3.0  # 左侧位置，更远离头部
            target_y = 15.0 + i * 0.8  # 从更高位置开始，每段增加0.8（更极端的向下）
            target_z = 2.0 + i * 0.1  # 更向前，远离眼睛
            
            # 设置修正后的位置
            corrected_pos = [target_x, target_y, target_z]
            
            # 重置旋转
            bone.rotX(0)
            bone.rotY(0)
            bone.rotZ(0)
            
            # 重置矩阵
            if hasattr(bone, 'reset_matrix'):
                bone.reset_matrix()
            
            # 完全重置骨骼变换矩阵
            bone.top_matrix = np.identity(4)
            bone.top_matrix[3, 0] = target_x
            bone.top_matrix[3, 1] = target_y
            bone.top_matrix[3, 2] = target_z
            
            bone.global_matrix = np.identity(4)
            bone.global_matrix[3, 0] = target_x
            bone.global_matrix[3, 1] = target_y
            bone.global_matrix[3, 2] = target_z
            
            # 重置所有旋转
            bone.delta_matrix = np.identity(4)
            bone.local_matrix = np.identity(4)
            
            # 直接设置修正后的位置
            if hasattr(bone, 'set_position'):
                bone.set_position(corrected_pos)
            elif hasattr(bone, 'setPosition'):
                bone.setPosition(corrected_pos[0], corrected_pos[1], corrected_pos[2])
            
            print(f"左侧骨骼 {bone.name} 修正后位置: {corrected_pos}")
        
        # 对右侧麻花辫骨骼，应用正确的位置
        for i, bone in enumerate(sorted(right_hair_bones, key=lambda b: int(b.name.split('_')[2]) if '_' in b.name and len(b.name.split('_')) >= 3 else 0)):
            # 获取当前位置
            current_pos = bone.get_position()
            
            # 设置正确的位置，从头部侧面开始自然下垂
            # 右侧麻花辫应该在头部右侧(X正值)，从头部高度(Y=15)开始下垂
            target_x = 3.0  # 右侧位置，更远离头部
            target_y = 15.0 + i * 0.8  # 从更高位置开始，每段增加0.8（更极端的向下）
            target_z = 2.0 + i * 0.1  # 更向前，远离眼睛
            
            # 设置修正后的位置
            corrected_pos = [target_x, target_y, target_z]
            
            # 重置旋转
            bone.rotX(0)
            bone.rotY(0)
            bone.rotZ(0)
            
            # 重置矩阵
            if hasattr(bone, 'reset_matrix'):
                bone.reset_matrix()
            
            # 完全重置骨骼变换矩阵
            bone.top_matrix = np.identity(4)
            bone.top_matrix[3, 0] = target_x
            bone.top_matrix[3, 1] = target_y
            bone.top_matrix[3, 2] = target_z
            
            bone.global_matrix = np.identity(4)
            bone.global_matrix[3, 0] = target_x
            bone.global_matrix[3, 1] = target_y
            bone.global_matrix[3, 2] = target_z
            
            # 重置所有旋转
            bone.delta_matrix = np.identity(4)
            bone.local_matrix = np.identity(4)
            
            # 直接设置修正后的位置
            if hasattr(bone, 'set_position'):
                bone.set_position(corrected_pos)
            elif hasattr(bone, 'setPosition'):
                bone.setPosition(corrected_pos[0], corrected_pos[1], corrected_pos[2])
            
            print(f"右侧骨骼 {bone.name} 修正后位置: {corrected_pos}")
        
        # 更新骨骼矩阵
        model.update_bone()
        
        print("麻花辫骨骼位置已修正到头部侧面")
    except Exception as e:
        print(f"修复麻花辫位置时出错: {e}")
        import traceback
        traceback.print_exc()

def reset_hair_position(model):
    """重置头发/麻花辫到默认位置"""
    if not hasattr(model, 'physics') or model.physics is None:
        return
    
    try:
        import pybullet
        
        # 查找头发相关的刚体
        hair_bodies = []
        for body in model.physics.bodies:
            if '髪' in body.name or 'hair' in body.name.lower() or '辫' in body.name:
                hair_bodies.append(body)
        
        print(f"重置 {len(hair_bodies)} 个头发相关刚体的位置...")
        
        # 对每个头发刚体，重置到其对应的骨骼位置
        for body in hair_bodies:
            if body.bone is not None:
                # 获取骨骼的当前位置
                bone_pos = body.bone.get_position()
                bone_quat = body.bone.get_quaternion()
                
                # 重置刚体位置到骨骼位置
                pybullet.resetBasePositionAndOrientation(
                    body.bid, 
                    bone_pos, 
                    bone_quat,
                    physicsClientId=model.physics.physics_engine
                )
                
                # 设置刚体速度为0，避免运动
                pybullet.resetBaseVelocity(
                    body.bid,
                    [0, 0, 0],
                    [0, 0, 0],
                    physicsClientId=model.physics.physics_engine
                )
                
                # 将刚体设置为静态，完全跟随骨骼
                pybullet.changeDynamics(
                    body.bid,
                    -1,
                    mass=0,  # 设置质量为0，使其变为静态
                    linearDamping=0,
                    angularDamping=0,
                    physicsClientId=model.physics.physics_engine
                )
        
        # 运行几次物理模拟，使刚体稳定
        for i in range(5):
            model.update_physics()
        
        print("头发位置重置完成，已设置为跟随骨骼")
    except Exception as e:
        print(f"重置头发位置时出错: {e}")
        import traceback
        traceback.print_exc()

def print_bone_info(model):
    """打印模型骨骼信息"""
    if not hasattr(model, 'bones'):
        print("模型没有骨骼信息")
        return [], []
    
    print("\n===== 骨骼信息 =====")
    print(f"总骨骼数: {len(model.bones)}")
    
    # 寻找头部和手臂骨骼
    head_bones = []
    arm_bones = []
    
    try:
        for bone in model.bones:
            bone_name = bone.name.lower()
            if 'head' in bone_name or '頭' in bone_name:
                head_bones.append(bone.name)
            elif 'arm' in bone_name or '腕' in bone_name or 'left' in bone_name or 'right' in bone_name or '左' in bone_name or '右' in bone_name:
                arm_bones.append(bone.name)
        
        print("\n可能的头部骨骼:")
        for bone_name in head_bones:
            print(f"  - {bone_name}")
        
        print("\n可能的手臂骨骼:")
        for bone_name in arm_bones:
            print(f"  - {bone_name}")
        
        print("\n所有骨骼列表:")
        for i, bone in enumerate(model.bones):
            print(f"  {i}: {bone.name}")
    except Exception as e:
        print(f"打印骨骼信息时出错: {e}")
    
    return head_bones, arm_bones

def smooth_interpolation(current, target, smoothing=0.08):
    """平滑插值函数，用于创建缓冲效果"""
    return current + (target - current) * smoothing

def ease_in_out_sine(t):
    """缓动函数：正弦缓入缓出"""
    return -(math.cos(math.pi * t) - 1) / 2

def animate_model(model, elapsed_time):
    """为模型添加平滑动画效果"""
    if not hasattr(model, 'bones'):
        print("模型没有骨骼信息，无法添加动画")
        return
    
    # 初始化骨骼状态存储
    if not hasattr(animate_model, 'bone_states'):
        animate_model.bone_states = {}
        animate_model.last_update_time = elapsed_time
    
    # 计算实际时间差
    actual_time_delta = elapsed_time - animate_model.last_update_time
    animate_model.last_update_time = elapsed_time
    
    # 寻找所有重要骨骼
    head_bones = []
    left_arm_bones = []
    right_arm_bones = []
    body_bones = []
    left_leg_bones = []
    right_leg_bones = []
    
    # 直接使用骨骼名称查找，确保找到正确的骨骼
    for bone in model.bones:
        # 跳过麻花辫骨骼，不应用动画
        if 'MaWei' in bone.name or '麻花' in bone.name or '辫' in bone.name:
            continue
            
        # 头部骨骼
        if bone.name == '頭':
            head_bones.append(bone)
        
        # 左臂骨骼
        elif bone.name == '左腕':
            left_arm_bones.append(bone)
        elif bone.name == '左肘':
            left_arm_bones.append(bone)
        elif bone.name == '左肩':
            left_arm_bones.append(bone)
        
        # 右臂骨骼
        elif bone.name == '右腕':
            right_arm_bones.append(bone)
        elif bone.name == '右肘':
            right_arm_bones.append(bone)
        elif bone.name == '右肩':
            right_arm_bones.append(bone)
        
        # 身体骨骼
        elif '上半身' in bone.name or '腰' in bone.name or 'センター' in bone.name:
            body_bones.append(bone)
        
        # 左腿骨骼
        elif '左足' in bone.name or '左ひざ' in bone.name or '左腿' in bone.name:
            left_leg_bones.append(bone)
        
        # 右腿骨骼
        elif '右足' in bone.name or '右ひざ' in bone.name or '右腿' in bone.name:
            right_leg_bones.append(bone)
    
    # 头部动画 - 随机目标点位平滑移动
    if head_bones:
        for bone in head_bones:
            try:
                # 获取骨骼的唯一标识
                bone_id = f"head_{bone.name}"
                
                # 初始化骨骼状态
                if bone_id not in animate_model.bone_states:
                    current_euler = bone.get_euler('xyz')
                    animate_model.bone_states[bone_id] = {
                        'current_x': current_euler[0],
                        'current_y': current_euler[1],
                        'current_z': current_euler[2],
                        'target_x': (random.random() - 0.5) * 0.3,  # 初始目标
                        'target_y': (random.random() - 0.5) * 0.2,  # 初始目标
                        'target_z': current_euler[2],
                        'next_target_time': elapsed_time + 2.0 + random.random() * 2.0,  # 2-4秒后更换目标
                        'phase': random.random() * math.pi * 2,  # 随机相位
                        'frequency': 0.5 + random.random() * 0.5,  # 随机频率
                        'amplitude_x': 0.1 + random.random() * 0.1,  # 随机振幅
                        'amplitude_y': 0.05 + random.random() * 0.05  # 随机振幅
                    }
                
                # 获取当前状态
                state = animate_model.bone_states[bone_id]
                
                # 检查是否需要生成新的目标点位
                if elapsed_time >= state['next_target_time']:
                    # 生成随机目标点位
                    state['target_x'] = (random.random() - 0.5) * 0.3  # -0.15到0.15
                    state['target_y'] = (random.random() - 0.5) * 0.2  # -0.1到0.1
                    state['next_target_time'] = elapsed_time + 2.0 + random.random() * 2.0  # 2-4秒后更换目标
                
                # 使用缓动函数计算平滑移动
                time_factor = min(1.0, actual_time_delta * 2.0)  # 限制时间因子，防止过度移动
                
                # 添加细微的呼吸感动作
                breathing = math.sin(elapsed_time * state['frequency'] + state['phase']) * 0.02
                
                # 计算X轴移动
                diff_x = state['target_x'] - state['current_x']
                move_x = diff_x * time_factor * 0.1 + breathing * state['amplitude_x']
                
                # 计算Y轴移动
                diff_y = state['target_y'] - state['current_y']
                move_y = diff_y * time_factor * 0.1 + breathing * state['amplitude_y']
                
                # 更新当前位置
                state['current_x'] += move_x
                state['current_y'] += move_y
                
                # 应用新的旋转
                bone.rotX(state['current_x'])
                bone.rotY(state['current_y'])
                
            except Exception as e:
                print(f"头部骨骼动画出错: {e}")
    
    # 身体动画 - 轻微摇摆和呼吸
    if body_bones:
        for bone in body_bones:
            try:
                # 获取骨骼的唯一标识
                bone_id = f"body_{bone.name}"
                
                # 初始化骨骼状态
                if bone_id not in animate_model.bone_states:
                    current_euler = bone.get_euler('xyz')
                    animate_model.bone_states[bone_id] = {
                        'current_x': current_euler[0],
                        'current_y': current_euler[1],
                        'current_z': current_euler[2],
                        'phase': random.random() * math.pi * 2,  # 随机相位
                        'frequency': 0.3 + random.random() * 0.2,  # 随机频率
                        'amplitude': 0.02 + random.random() * 0.02  # 随机振幅
                    }
                
                # 获取当前状态
                state = animate_model.bone_states[bone_id]
                
                # 计算呼吸和轻微摇摆
                breathing = math.sin(elapsed_time * state['frequency'] + state['phase']) * state['amplitude']
                sway = math.cos(elapsed_time * state['frequency'] * 0.7 + state['phase']) * state['amplitude'] * 0.5
                
                # 应用新的旋转
                bone.rotX(state['current_x'] + breathing)
                bone.rotY(state['current_y'] + sway)
                
            except Exception as e:
                print(f"身体骨骼动画出错: {e}")
    
    # 左臂动画 - 更自然的挥手动作
    if left_arm_bones:
        for bone in left_arm_bones:
            try:
                # 获取骨骼的唯一标识
                bone_id = f"left_arm_{bone.name}"
                
                # 初始化骨骼状态
                if bone_id not in animate_model.bone_states:
                    current_euler = bone.get_euler('xyz')
                    animate_model.bone_states[bone_id] = {
                        'current_x': current_euler[0],
                        'current_y': current_euler[1],
                        'current_z': current_euler[2],
                        'phase': random.random() * math.pi * 2,  # 随机相位
                        'frequency': 0.4 + random.random() * 0.3,  # 随机频率
                        'amplitude_x': 0.1 + random.random() * 0.05,  # X轴振幅
                        'amplitude_y': 0.05 + random.random() * 0.03,  # Y轴振幅
                        'amplitude_z': 0.15 + random.random() * 0.1,  # Z轴振幅
                        'gesture_time': elapsed_time + random.random() * 5.0,  # 下一个手势时间
                        'gesture_type': random.choice(['wave', 'swing', 'idle'])  # 手势类型
                    }
                
                # 获取当前状态
                state = animate_model.bone_states[bone_id]
                
                # 检查是否需要更换手势
                if elapsed_time >= state['gesture_time']:
                    state['gesture_type'] = random.choice(['wave', 'swing', 'idle'])
                    state['gesture_time'] = elapsed_time + 3.0 + random.random() * 4.0  # 3-7秒后更换手势
                
                # 根据手势类型计算动画
                if state['gesture_type'] == 'wave':
                    # 挥手动作
                    wave = math.sin(elapsed_time * 2.0 + state['phase']) * state['amplitude_z']
                    sway = math.cos(elapsed_time * 0.8 + state['phase']) * state['amplitude_x'] * 0.5
                    
                    # 应用新的旋转
                    bone.rotX(state['current_x'] + sway)
                    bone.rotZ(state['current_z'] + wave)
                    
                elif state['gesture_type'] == 'swing':
                    # 摆动动作
                    swing = math.sin(elapsed_time * state['frequency'] + state['phase']) * state['amplitude_x']
                    lift = math.sin(elapsed_time * state['frequency'] * 0.5 + state['phase']) * state['amplitude_y']
                    
                    # 应用新的旋转
                    bone.rotX(state['current_x'] + swing)
                    bone.rotY(state['current_y'] + lift)
                    
                else:  # idle
                    # 静止状态，只有轻微呼吸
                    breathing = math.sin(elapsed_time * state['frequency'] * 0.3 + state['phase']) * 0.02
                    
                    # 应用新的旋转
                    bone.rotX(state['current_x'] + breathing)
                    bone.rotZ(state['current_z'] + breathing * 0.5)
                
            except Exception as e:
                print(f"左臂骨骼动画出错: {e}")
    
    # 右臂动画 - 更自然的挥手动作
    if right_arm_bones:
        for bone in right_arm_bones:
            try:
                # 获取骨骼的唯一标识
                bone_id = f"right_arm_{bone.name}"
                
                # 初始化骨骼状态
                if bone_id not in animate_model.bone_states:
                    current_euler = bone.get_euler('xyz')
                    animate_model.bone_states[bone_id] = {
                        'current_x': current_euler[0],
                        'current_y': current_euler[1],
                        'current_z': current_euler[2],
                        'phase': random.random() * math.pi * 2,  # 随机相位
                        'frequency': 0.4 + random.random() * 0.3,  # 随机频率
                        'amplitude_x': 0.1 + random.random() * 0.05,  # X轴振幅
                        'amplitude_y': 0.05 + random.random() * 0.03,  # Y轴振幅
                        'amplitude_z': 0.15 + random.random() * 0.1,  # Z轴振幅
                        'gesture_time': elapsed_time + random.random() * 5.0,  # 下一个手势时间
                        'gesture_type': random.choice(['wave', 'swing', 'idle'])  # 手势类型
                    }
                
                # 获取当前状态
                state = animate_model.bone_states[bone_id]
                
                # 检查是否需要更换手势
                if elapsed_time >= state['gesture_time']:
                    state['gesture_type'] = random.choice(['wave', 'swing', 'idle'])
                    state['gesture_time'] = elapsed_time + 3.0 + random.random() * 4.0  # 3-7秒后更换手势
                
                # 根据手势类型计算动画
                if state['gesture_type'] == 'wave':
                    # 挥手动作
                    wave = math.sin(elapsed_time * 2.0 + state['phase']) * state['amplitude_z']
                    sway = math.cos(elapsed_time * 0.8 + state['phase']) * state['amplitude_x'] * 0.5
                    
                    # 应用新的旋转
                    bone.rotX(state['current_x'] + sway)
                    bone.rotZ(state['current_z'] + wave)
                    
                elif state['gesture_type'] == 'swing':
                    # 摆动动作
                    swing = math.sin(elapsed_time * state['frequency'] + state['phase']) * state['amplitude_x']
                    lift = math.sin(elapsed_time * state['frequency'] * 0.5 + state['phase']) * state['amplitude_y']
                    
                    # 应用新的旋转
                    bone.rotX(state['current_x'] + swing)
                    bone.rotY(state['current_y'] + lift)
                    
                else:  # idle
                    # 静止状态，只有轻微呼吸
                    breathing = math.sin(elapsed_time * state['frequency'] * 0.3 + state['phase']) * 0.02
                    
                    # 应用新的旋转
                    bone.rotX(state['current_x'] + breathing)
                    bone.rotZ(state['current_z'] + breathing * 0.5)
                
            except Exception as e:
                print(f"右臂骨骼动画出错: {e}")
    
    # 腿部动画 - 轻微的站立摇摆
    if left_leg_bones:
        for bone in left_leg_bones:
            try:
                # 获取骨骼的唯一标识
                bone_id = f"left_leg_{bone.name}"
                
                # 初始化骨骼状态
                if bone_id not in animate_model.bone_states:
                    current_euler = bone.get_euler('xyz')
                    animate_model.bone_states[bone_id] = {
                        'current_x': current_euler[0],
                        'current_y': current_euler[1],
                        'current_z': current_euler[2],
                        'phase': random.random() * math.pi * 2,  # 随机相位
                        'frequency': 0.2 + random.random() * 0.1,  # 随机频率
                        'amplitude': 0.01 + random.random() * 0.01  # 随机振幅
                    }
                
                # 获取当前状态
                state = animate_model.bone_states[bone_id]
                
                # 计算轻微的摇摆
                sway = math.sin(elapsed_time * state['frequency'] + state['phase']) * state['amplitude']
                shift = math.cos(elapsed_time * state['frequency'] * 0.7 + state['phase']) * state['amplitude'] * 0.5
                
                # 应用新的旋转
                bone.rotX(state['current_x'] + sway)
                bone.rotY(state['current_y'] + shift)
                
            except Exception as e:
                print(f"左腿骨骼动画出错: {e}")
    
    # 右腿动画 - 轻微的站立摇摆
    if right_leg_bones:
        for bone in right_leg_bones:
            try:
                # 获取骨骼的唯一标识
                bone_id = f"right_leg_{bone.name}"
                
                # 初始化骨骼状态
                if bone_id not in animate_model.bone_states:
                    current_euler = bone.get_euler('xyz')
                    animate_model.bone_states[bone_id] = {
                        'current_x': current_euler[0],
                        'current_y': current_euler[1],
                        'current_z': current_euler[2],
                        'phase': random.random() * math.pi * 2,  # 随机相位
                        'frequency': 0.2 + random.random() * 0.1,  # 随机频率
                        'amplitude': 0.01 + random.random() * 0.01  # 随机振幅
                    }
                
                # 获取当前状态
                state = animate_model.bone_states[bone_id]
                
                # 计算轻微的摇摆（与左腿相反相位）
                sway = -math.sin(elapsed_time * state['frequency'] + state['phase']) * state['amplitude']
                shift = -math.cos(elapsed_time * state['frequency'] * 0.7 + state['phase']) * state['amplitude'] * 0.5
                
                # 应用新的旋转
                bone.rotX(state['current_x'] + sway)
                bone.rotY(state['current_y'] + shift)
                
            except Exception as e:
                print(f"右腿骨骼动画出错: {e}")

def main():
    # 设置模型文件路径
    model_path = os.path.join("LTYAImodle", "LTYAImodle.pmx")
    
    # 检查模型文件是否存在
    if not os.path.exists(model_path):
        print(f"模型文件不存在: {model_path}")
        return
    
    # 创建世界（渲染窗口）- 使用自定义的CustomWorld类
    print("创建世界...")
    world = CustomWorld("洛天依模型查看器", 800, 600)
    print("世界创建完成")
    
    # 创建模型实例
    model = mmdpy.model()
    
    # 加载模型
    if not model.load(model_path):
        print("模型加载失败")
        return
    
    # 检查物理功能并禁用
    if hasattr(model.model, 'physics') and model.model.physics is not None:
        print("检测到物理功能，但为了解决麻花辫位置问题，已禁用物理系统")
        # 完全禁用物理系统，使用骨骼动画代替
        model.model.physics = None
    
    print(f"成功加载模型: {model_path}")
    print(f"模型类型: {model.file_type}")
    
    # 显示模型基本信息
    try:
        print(f"顶点数: {len(model.model.vertices) if hasattr(model.model, 'vertices') else '未知'}")
        print(f"网格数: {len(model.model.meshes) if hasattr(model.model, 'meshes') else '未知'}")
        print(f"骨骼数: {len(model.model.bones) if hasattr(model.model, 'bones') else '未知'}")
    except Exception as e:
        print(f"获取模型信息时出错: {e}")
    
    # 打印骨骼信息
    head_bones, arm_bones = print_bone_info(model.model)
    
    print("\n使用骨骼动画代替物理系统，确保麻花辫在正确位置")
    
    # 将模型添加到世界中
    world.push(model)
    
    # 主循环
    print("开始渲染，按ESC键退出")
    try:
        frame_count = 0
        
        # 预先找到所有麻花辫骨骼
        hair_bones = []
        for bone in model.model.bones:
            if 'MaWei_L' in bone.name or 'MaWei_R' in bone.name:
                hair_bones.append(bone)
        
        print(f"找到 {len(hair_bones)} 个麻花辫相关骨骼")
        
        # 创建麻花辫物理模拟器
        hair_physics = HairPhysicsSimulator()
        hair_physics.init_hair_segments(hair_bones)
        
        # 初始修复麻花辫位置
        fix_hair_bones_position(model.model)
        
        while True:
            # 计算经过的时间
            current_time = time.time()
            elapsed_time = current_time - world.start_time
            
            # 每帧都更新动画，提高流畅度
            # 添加平滑动画效果
            animate_model(model.model, elapsed_time)
            
            # 更新麻花辫物理模拟
            hair_physics.update(0.016)  # 假设60FPS，每帧约16ms
            
            # 更新骨骼
            model.model.update_bone()
            
            # 再次更新骨骼矩阵，确保修改生效
            model.model.update_bone()
            
            # 执行渲染
            if world.run():
                break
            
            frame_count += 1
    except Exception as e:
        print(f"渲染过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 清理资源
    try:
        world.close()
    except Exception as e:
        print(f"清理资源时出错: {e}")
    
    print("程序结束")

if __name__ == "__main__":
    main()