#!/usr/bin/env python3
"""基础功能测试脚本"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """测试关键模块导入"""
    print("=" * 50)
    print("测试1: 模块导入")
    print("=" * 50)
    
    try:
        import DyberPet.settings as settings
        print("✅ settings模块导入成功")
    except Exception as e:
        print(f"❌ settings模块导入失败: {e}")
        return False
    
    try:
        from DyberPet.conf import PetConfig, ItemData
        print("✅ conf模块导入成功")
    except Exception as e:
        print(f"❌ conf模块导入失败: {e}")
        return False
    
    try:
        from DyberPet.llm.llm_client import LLMClient
        from DyberPet.llm.llm_request_manager import LLMRequestManager
        print("✅ LLM模块导入成功")
    except Exception as e:
        print(f"❌ LLM模块导入失败: {e}")
        return False
    
    try:
        from DyberPet.mouse_utils import MouseMoveManager
        print("✅ mouse_utils模块导入成功")
    except Exception as e:
        print(f"❌ mouse_utils模块导入失败: {e}")
        return False
    
    try:
        from DyberPet.Dashboard.DashboardUI import DashboardMainWindow
        print("✅ Dashboard模块导入成功")
    except Exception as e:
        print(f"❌ Dashboard模块导入失败: {e}")
        return False
    
    print()
    return True

def test_deleted_modules():
    """测试已删除模块确实不存在"""
    print("=" * 50)
    print("测试2: 已删除模块验证")
    print("=" * 50)
    
    deleted_modules = [
        ('DyberPet.Dashboard.shopUI', '商店系统'),
        ('DyberPet.Dashboard.taskUI', '任务系统'),
        ('DyberPet.Dashboard.animDesignUI', '动画设计器'),
        ('DyberPet.Accessory', '附件系统'),
    ]
    
    all_deleted = True
    for module_name, desc in deleted_modules:
        try:
            __import__(module_name)
            print(f"❌ {desc}({module_name})仍然存在")
            all_deleted = False
        except ImportError:
            print(f"✅ {desc}({module_name})已成功删除")
    
    print()
    return all_deleted

def test_settings_init():
    """测试settings初始化"""
    print("=" * 50)
    print("测试3: Settings初始化")
    print("=" * 50)
    
    try:
        import DyberPet.settings as settings
        settings.init()
        print(f"✅ Settings初始化成功")
        print(f"   - 宠物列表: {len(settings.pets)}个")
        print(f"   - 默认宠物: {settings.default_pet}")
        print(f"   - 语言: {settings.language_code}")
        print()
        return True
    except Exception as e:
        print(f"❌ Settings初始化失败: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False

def test_llm_modules():
    """测试LLM模块基本功能"""
    print("=" * 50)
    print("测试4: LLM模块基本功能")
    print("=" * 50)
    
    try:
        from DyberPet.llm.types import EventType, EventPriority
        from DyberPet.llm.constants import ERROR_MESSAGES, LLM_CONFIG_DEFAULT
        from DyberPet.llm.error_handler import ErrorHandler
        
        print("✅ LLM类型定义正常")
        print(f"   - 事件类型数: {len([e for e in EventType])}")
        print(f"   - 优先级数: {len([p for p in EventPriority])}")
        
        # 测试错误处理器
        handler = ErrorHandler("zh_CN")
        msg, details, error_type = handler.get_error_info({"code": "E001", "details": "测试"})
        print(f"✅ 错误处理器正常")
        print(f"   - 测试错误消息: {msg}")
        
        print()
        return True
    except Exception as e:
        print(f"❌ LLM模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False

def test_file_structure():
    """测试文件结构"""
    print("=" * 50)
    print("测试5: 文件结构检查")
    print("=" * 50)
    
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
    ]
    
    deleted_files = [
        'DyberPet/Dashboard/shopUI.py',
        'DyberPet/Dashboard/taskUI.py',
        'DyberPet/Dashboard/animDesignUI.py',
        'DyberPet/Accessory.py',
    ]
    
    all_good = True
    
    print("检查必需文件:")
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} 不存在")
            all_good = False
    
    print("\n检查已删除文件:")
    for file_path in deleted_files:
        if not os.path.exists(file_path):
            print(f"✅ {file_path} 已删除")
        else:
            print(f"❌ {file_path} 仍然存在")
            all_good = False
    
    print()
    return all_good

def main():
    """运行所有测试"""
    print("\n" + "=" * 50)
    print("DyberPet 基础功能测试")
    print("=" * 50 + "\n")
    
    results = []
    
    # 运行测试
    results.append(("模块导入", test_imports()))
    results.append(("已删除模块验证", test_deleted_modules()))
    results.append(("Settings初始化", test_settings_init()))
    results.append(("LLM模块功能", test_llm_modules()))
    results.append(("文件结构检查", test_file_structure()))
    
    # 总结
    print("=" * 50)
    print("测试总结")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed}个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
