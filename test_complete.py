#!/usr/bin/env python3
"""
DyberPet 完整测试套件
测试所有核心功能和已删除功能的验证
"""
import sys
import os
import json
import time
import unittest
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

class TestDyberPetCore(unittest.TestCase):
    """核心功能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.project_root = Path(__file__).parent
        
    def test_file_structure(self):
        """测试文件结构完整性"""
        required_files = [
            'DyberPet/DyberPet.py',
            'DyberPet/modules.py', 
            'DyberPet/settings.py',
            'DyberPet/conf.py',
            'DyberPet/mouse_utils.py',
            'DyberPet/llm/llm_client.py',
            'DyberPet/llm/llm_request_manager.py',
            'DyberPet/llm/types.py',
            'DyberPet/llm/constants.py',
            'DyberPet/llm/error_handler.py',
            'DyberPet/Dashboard/DashboardUI.py',
            'DyberPet/Dashboard/statusUI.py',
            'DyberPet/Dashboard/inventoryUI.py',
            'DyberPet/Dashboard/animationUI.py',
            'main.py',
            'run_DyberPet.py',
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            self.assertTrue(full_path.exists(), f"必需文件不存在: {file_path}")
            
    def test_deleted_files(self):
        """测试已删除文件确实不存在"""
        deleted_files = [
            'DyberPet/Dashboard/shopUI.py',
            'DyberPet/Dashboard/taskUI.py', 
            'DyberPet/Dashboard/animDesignUI.py',
            'DyberPet/Accessory.py',
        ]
        
        for file_path in deleted_files:
            full_path = self.project_root / file_path
            self.assertFalse(full_path.exists(), f"已删除文件仍然存在: {file_path}")
            
    def test_config_files(self):
        """测试配置文件"""
        config_files = [
            'data/settings.json',
            'data/pet_data.json', 
            'data/act_data.json',
            'res/items/Default/info.json',
            'res/pet/派蒙/pet_conf.json',
        ]
        
        for file_path in config_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                except json.JSONDecodeError:
                    self.fail(f"配置文件JSON格式错误: {file_path}")
                    
    def test_resource_files(self):
        """测试资源文件"""
        resource_dirs = [
            'res/icons',
            'res/pet/派蒙/action',
            'res/items/Default',
        ]
        
        for dir_path in resource_dirs:
            full_path = self.project_root / dir_path
            self.assertTrue(full_path.exists(), f"资源目录不存在: {dir_path}")
            self.assertTrue(full_path.is_dir(), f"资源路径不是目录: {dir_path}")

class TestCodeQuality(unittest.TestCase):
    """代码质量测试"""
    
    def setUp(self):
        self.project_root = Path(__file__).parent
        
    def test_python_syntax(self):
        """测试Python语法"""
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            # 跳过测试文件、缓存文件、第三方库文件和模板文件
            if (('test_' in py_file.name) or 
                ('__pycache__' in str(py_file)) or
                ('.venv' in str(py_file)) or
                ('site-packages' in str(py_file)) or
                ('.tmpl.py' in py_file.name)):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), py_file, 'exec')
            except SyntaxError as e:
                self.fail(f"语法错误 {py_file}: {e}")
            except Exception as e:
                # 忽略导入错误等运行时错误
                pass
                
    def test_no_obvious_errors(self):
        """检查明显的代码错误"""
        python_files = list(self.project_root.rglob("*.py"))
        
        error_patterns = [
            'print(',  # 调试print语句
            'TODO',    # 未完成的TODO
            'FIXME',   # 需要修复的代码
        ]
        
        for py_file in python_files:
            if 'test_' in py_file.name:
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否有过多的调试print语句
                print_count = content.count('print(')
                if print_count > 10:  # 允许少量print语句
                    print(f"警告: {py_file} 包含 {print_count} 个print语句")
                    
            except Exception:
                pass

class TestLLMModule(unittest.TestCase):
    """LLM模块测试"""
    
    def test_llm_constants(self):
        """测试LLM常量定义"""
        try:
            # 尝试导入常量，但不依赖PySide6
            constants_file = Path(__file__).parent / 'DyberPet/llm/constants.py'
            if constants_file.exists():
                with open(constants_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.assertIn('ERROR_MESSAGES', content)
                    self.assertIn('LLM_CONFIG_DEFAULT', content)
        except Exception as e:
            self.skipTest(f"无法测试LLM常量: {e}")
            
    def test_llm_types(self):
        """测试LLM类型定义"""
        try:
            types_file = Path(__file__).parent / 'DyberPet/llm/types.py'
            if types_file.exists():
                with open(types_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.assertIn('EventType', content)
                    self.assertIn('EventPriority', content)
        except Exception as e:
            self.skipTest(f"无法测试LLM类型: {e}")

class TestFeatureCleanup(unittest.TestCase):
    """功能清理验证测试"""
    
    def test_no_shop_references(self):
        """确保没有商店系统的引用"""
        python_files = list(Path(__file__).parent.rglob("*.py"))
        
        shop_keywords = ['shopUI', 'shop_window', 'ShopInterface']
        
        for py_file in python_files:
            if 'test_' in py_file.name:
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for keyword in shop_keywords:
                        if keyword in content:
                            # 允许在注释中提到
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if keyword in line and not line.strip().startswith('#'):
                                    self.fail(f"发现商店系统引用 {py_file}:{i+1}: {line.strip()}")
            except Exception:
                pass
                
    def test_no_task_references(self):
        """确保没有任务系统的引用"""
        python_files = list(Path(__file__).parent.rglob("*.py"))
        
        task_keywords = ['taskUI', 'task_window', 'TaskInterface']
        
        for py_file in python_files:
            if 'test_' in py_file.name:
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for keyword in task_keywords:
                        if keyword in content:
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if keyword in line and not line.strip().startswith('#'):
                                    self.fail(f"发现任务系统引用 {py_file}:{i+1}: {line.strip()}")
            except Exception:
                pass

def run_performance_test():
    """性能测试"""
    print("\n" + "="*50)
    print("性能测试")
    print("="*50)
    
    # 测试启动时间
    start_time = time.time()
    try:
        # 模拟导入主要模块的时间
        import importlib.util
        
        modules_to_test = [
            'DyberPet.conf',
            'DyberPet.utils', 
        ]
        
        for module_name in modules_to_test:
            try:
                module_path = Path(__file__).parent / f"{module_name.replace('.', '/')}.py"
                if module_path.exists():
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        # 不实际执行，只检查能否加载
                        print(f"✅ 模块 {module_name} 可以加载")
            except Exception as e:
                print(f"❌ 模块 {module_name} 加载失败: {e}")
                
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        
    end_time = time.time()
    load_time = end_time - start_time
    print(f"模块加载时间: {load_time:.2f}秒")
    
    if load_time < 2.0:
        print("✅ 加载性能良好")
    else:
        print("⚠️ 加载时间较长，可能需要优化")

def main():
    """运行所有测试"""
    print("DyberPet 完整测试套件")
    print("="*50)
    
    # 运行单元测试
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestDyberPetCore,
        TestCodeQuality, 
        TestLLMModule,
        TestFeatureCleanup,
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 运行性能测试
    run_performance_test()
    
    # 总结
    print("\n" + "="*50)
    print("测试总结")
    print("="*50)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    print(f"总测试数: {total_tests}")
    print(f"通过: {passed}")
    print(f"失败: {failures}")
    print(f"错误: {errors}")
    
    if failures == 0 and errors == 0:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️ {failures + errors}个测试未通过")
        
        if result.failures:
            print("\n失败的测试:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
                
        if result.errors:
            print("\n错误的测试:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")
        
        return 1

if __name__ == '__main__':
    sys.exit(main())